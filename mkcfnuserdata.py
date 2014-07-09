#!/usr/bin/env python
#
# mkcfnuserdata.py
#
# ATonns Wed May  1 16:51:58 EDT 2013
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
import json
import re
progname = "mkcfnuserdata.py"
if __name__ == '__main__':
    # setup arguments
    parser = argparse.ArgumentParser(
        prog=progname,
        description="JSON encodes a file as list of strings "
        "and parses it for CloudFormation Ref objects"
    )
    parser.add_argument(
        "filenames",
        help="files to encode", nargs='*'
    )
    args = parser.parse_args()
    # prep regular expressions
    shebang = re.compile('^#\!.*$')
    commentLine = re.compile('^\s*#.*')
    blankLine = re.compile('^$')
    # iterate on args
    for filename in args.filenames:
        lines = []
        with open(filename, 'r') as f:
            done = False
            while not done:
                # get a line
                line = f.readline()
                # if null, we're done
                if line == '':
                    break
                # skip lines that are not the first line
                # and either comment or blank
                s = shebang.match(line)
                c = commentLine.match(line)
                b = blankLine.match(line)
                if not s and (c or b):
                    continue
                # add the line to the array
                lines.append(line)
        # get the json
        j = json.dumps(lines, indent=1)
        # do a little templating for CloudFormation Refs
        print re.sub(
            r'CFNREF_([a-zA-Z_0-9]+)',
            r'", { "Ref": "\1" }, "',
            j
        )
