#!/usr/bin/env python
#
# asg-attic.py
#
# ATonns Fri Sep 27 11:28:52 EDT 2013
#
#   Copyright 2013 Corsis
#   http://www.corsis.com/
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import argparse
import time
from boto.cloudformation.connection import CloudFormationConnection
from boto.ec2.autoscale import AutoScaleConnection
from boto.exception import BotoServerError


def getStackAutoscalingGroupData(cfn, asg):
    data = {}
    # get the list of stacks
    done = False
    while not done:
        try:
            stacks = cfn.list_stacks()
        except:
            done = False
            time.sleep(0.25)
        else:
            done = True
    for stack in stacks:
        # we only care about stacks that haven't been deleted
        if stack.stack_status == "DELETE_COMPLETE":
            continue
        # get all the components of th stack
        done = False
        while not done:
            try:
                resources = cfn.list_stack_resources(stack.stack_id)
            except:
                done = False
                time.sleep(0.25)
            else:
                done = True
        for r in resources:
            # found an ASG! keep track of it
            if r.resource_type == "AWS::AutoScaling::AutoScalingGroup":
                data.setdefault(
                    stack.stack_name, []
                ).append(
                    {"name": r.physical_resource_id}
                )
        time.sleep(0.25)
    # collect the name of all the ASG
    asgnames = []
    for stackname in data:
        for asginfo in data[stackname]:
            asgnames.append(asginfo['name'])
    # query the details on them
    done = False
    while not done:
        try:
            asgroups = asg.get_all_groups(asgnames)
        except:
            done = False
            time.sleep(0.25)
        else:
            done = True
    # finalize the data
    for asgdata in asgroups:
        for stackname in data:
            for asginfo in data[stackname]:
                if asginfo['name'] == asgdata.name:
                    asginfo['min'] = asgdata.min_size
                    asginfo['max'] = asgdata.max_size
                    asginfo['desired'] = asgdata.desired_capacity
                    asginfo['asgdata'] = asgdata
    return data


def updateAutoScalingGroup(
    data,
    target_stack,
    target_min,
    target_max,
    target_desired,
):
    done = False
    for stackname in data:
        if stackname == target_stack:
            print "{s}:".format(
                s=stackname,
            )
            for asginfo in data[stackname]:
                asgdata = asginfo['asgdata']
                asgdata.min_size = target_min
                asgdata.max_size = target_max
                asgdata.desired_capacity = target_desired
                try:
                    asgdata.update()
                except BotoServerError as e:
                    print e.message
                else:
                    print "Autoscaling group {n} now has " \
                          "min {mn} max {mx} desired {d}". \
                          format(
                              n=asginfo['name'],
                              mn=target_min,
                              mx=target_max,
                              d=target_desired,
                          )
                    done = True
    if not done:
        print "Error updating autoscaling group(s) " \
              "in stack '{n}'".format(
                  n=target_stack,
              )


if __name__ == '__main__':
    # setup arguments and parse them
    parser = argparse.ArgumentParser(prog='asg-attic.py')
    parser.add_argument(
        "-l", "--list", action='store_true',
        help="list stacks, autoscaling groups and values"
    )
    parser.add_argument(
        "-m", "--mothball", type=str,
        help="reduce the instances for all autoscaling group(s) "
             "in a stack to zero"
    )
    parser.add_argument(
        "-r", "--reopen", nargs=2,
        help="increase the instances for all autoscaling group(s) "
             "in a stack to min:max:desired"
    )
    args = parser.parse_args()

    # connect to AWS
    try:
        cfn = CloudFormationConnection()
        asg = AutoScaleConnection()
    except:
        print "AWS connect error"
    else:
        # get the key data
        data = getStackAutoscalingGroupData(cfn, asg)
        # list if explicitly listing or not doing anything else
        if args.list or args.mothball is None and args.reopen is None:
            for stackname in sorted(data, key=data.__getitem__):
                print "{s}:".format(
                    s=stackname,
                )
                for asginfo in data[stackname]:
                    print "    {n} {mn}:{mx}:{d}".format(
                        n=asginfo['name'],
                        mn=asginfo['min'],
                        mx=asginfo['max'],
                        d=asginfo['desired'],
                    )
        else:
            # mothball an autoscaling group
            if args.mothball is not None:
                target_stack = args.mothball
                updateAutoScalingGroup(data, target_stack, 0, 0, 0)
            # reopen an autoscaling group
            elif args.reopen is not None:
                # get the names and values
                target_stack = args.reopen[0]
                values = args.reopen[1]
                # get the min:max:desired
                target_vals = values.split(':')
                if len(target_vals) != 3:
                    # invalid min:max:desired
                    print "Invalid min:max:desired for " \
                          "autoscaling groups: {v}".format(
                              v=values,
                          )
                else:
                    target_min = target_vals[0]
                    target_max = target_vals[1]
                    target_desired = target_vals[2]
                    updateAutoScalingGroup(
                        data,
                        target_stack,
                        target_min,
                        target_max,
                        target_desired,
                    )
