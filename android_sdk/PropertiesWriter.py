#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
"""See docstring for PropertiesWriter class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from __future__ import absolute_import

import ConfigParser
from collections import OrderedDict

from autopkglib import Processor, ProcessorError

__all__ = ["PropertiesWriter"]


# this code stolen from http://stackoverflow.com/a/25084055
class EqualsSpaceRemover:
    output_file = None

    def __init__(self, new_output_file):
        self.output_file = new_output_file

    def write(self, what):
        self.output_file.write(what.replace(" = ", "="))


class PropertiesWriter(Processor):
    # pylint: disable=missing-docstring
    description = "Read the version.properties file inside the " "SQLDeveloper.app."
    input_variables = {
        "file_path": {
            "required": True,
            "description": "Path to source.properties file to create.",
        },
        "properties": {
            "required": True,
            "description": "Dictionary of keys/values to write to file.",
        },
    }
    output_variables = {}

    __doc__ = description

    def main(self):
        cp = ConfigParser.SafeConfigParser()
        cp.optionxform = str

        sort = sorted(self.env["properties"].items(), key=lambda t: t[0])
        properties = OrderedDict(sort)

        for key, value in properties.iteritems():
            cp.set("", str(key), value)
        # Write the file out
        with open(self.env["file_path"], "wb") as f:
            try:
                cp.write(EqualsSpaceRemover(f))
            except IOError as err:
                raise ProcessorError(err)
        # Now delete the first line, the section header
        with open(self.env["file_path"], "rb") as old:
            lines = old.readlines()
        lines[0] = "# Generated by AutoPkg\n"
        with open(self.env["file_path"], "wb") as new:
            for line in lines:
                new.write(line)


if __name__ == "__main__":
    PROCESSOR = PropertiesWriter()
    PROCESSOR.execute_shell()
