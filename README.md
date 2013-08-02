## CloudFormation Helpers

Some scripts to help you create [AWS CloudFormation](http://aws.amazon.com/cloudformation/) templates

### mkcfnuserdata.py

This script will help JSON format a script so that it can be embedded as in the `UserData`
property for a [`AWS::EC2::Instance`](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html)
or [`AWS::AutoScaling::LaunchConfiguration`](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-launchconfig.html) resources.
It does the following things:

 - removes blank lines
 - removes comment lines that start with '#' **but** keeps the shebang line
 - does ghetto templating with the `CFNREF_` prefix:
    turn `CFNREF_CustomParameter` into `", { "Ref": "CustomParameter" }, "`

Once you do this, you can copy/paste the results into your template.
 
#### ToDo:

 - better templating for [`Ref`](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html) and possibly [`Fn::GetAtt`](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html)
 - don't copy/paste results into a template, take a template as an argument and use templating
 - include more [cloud-init](http://cloudinit.readthedocs.org/en/latest/topics/format.html) features, formats

### License

Copyright 2013 Corsis
http://www.corsis.com/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

