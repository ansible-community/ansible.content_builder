# Copyright (c) 2023 Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pathlib
import re
from typing import Dict, List, Optional, TypedDict
import boto3
import json
import yaml
from ansible_collections.ansible.content_builder.plugins.plugin_utils.cloud_utils import (
    generator,
    utils,
)
from ansible.plugins.action import ActionBase


class Schema(TypedDict):
    """A type for the JSONSchema spec"""

    typeName: str
    description: str
    properties: Dict
    definitions: Optional[Dict]
    required: Optional[List]
    primaryIdentifier: List
    readOnlyProperties: Optional[List]
    createOnlyProperties: Optional[List]
    taggable: Optional[bool]
    handlers: Optional[Dict]


def generate_schema(raw_content) -> Dict:
    json_content = json.loads(raw_content)
    schema: Dict[str, Schema] = json_content
    return schema


class ActionModule(ActionBase):
    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._validator_name = None
        self._result = {}

    def _debug(self, name, msg):
        """Output text using ansible's display
        :param msg: The message
        :type msg: str
        """
        msg = "<{phost}> {name} {msg}".format(phost=self._playhost, name=name, msg=msg)
        self._display.vvvv(msg)

    def run(self, tmp=None, task_vars=None):
        """The std execution entry pt for an action plugin
        :param tmp: no longer used
        :type tmp: none
        :param task_vars: The vars provided when the task is run
        :type task_vars: dict
        :return: The results from the parser
        :rtype: dict
        """

        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._task_vars = task_vars

        args = self._task.args
        resource_file = pathlib.Path(args.get("resource") + "/modules.yaml")

        RESOURCES = yaml.load(
            pathlib.Path(resource_file).read_text(), Loader=yaml.FullLoader
        )

        for module in RESOURCES:
            for k, v in module.items():
                type_name = v["resource"]
            print("Collecting Schema")
            print(type_name)
            cloudformation = generator.CloudFormationWrapper(
                boto3.client("cloudformation")
            )
            raw_content = cloudformation.generate_docs(type_name)
            schema = generate_schema(raw_content)
            file_name = re.sub("::", "_", type_name)
            if not pathlib.Path(args.get("api_object_path")).exists():
                pathlib.Path(args.get("api_object_path")).mkdir(
                    parents=True, exist_ok=True
                )
            schema_file = pathlib.Path(
                args.get("api_object_path") + "/" + file_name + ".json"
            )
            schema_file.write_text(json.dumps(schema, indent=2))
        return self._result
