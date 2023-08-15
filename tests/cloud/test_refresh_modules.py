# (c) 2022 Red Hat Inc.
#
# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import os
import json
from pathlib import Path
import ansible_collections.ansible.content_builder.plugins.plugin_utils.cloud_utils.generator as g
import ansible_collections.ansible.content_builder.plugins.action.generate_cloud_modules as rm
import ansible_collections.ansible.content_builder.plugins.action.generate_cloud_schema as rs


def resources(filepath):
    current = Path(os.path.dirname(os.path.abspath(__file__)))
    with open(current / filepath) as fp:
        return json.load(fp)


raw_content = resources("fixtures/raw_content.json")
expected_content = resources("fixtures/expected_content.json")


def test__gen_required_if():
    expected_required_if = [
        ["state", "present", ["log_group_name"], True],
        ["state", "absent", ["log_group_name"], True],
        ["state", "get", ["log_group_name"], True],
    ]
    schema = rs.generate_schema(json.dumps(raw_content))
    assert rm.gen_required_if(schema) == expected_required_if


def test__generate_params():
    expected_params = """
params['kms_key_id'] = module.params.get('kms_key_id')
params['log_group_name'] = module.params.get('log_group_name')
params['retention_in_days'] = module.params.get('retention_in_days')
params['tags'] = module.params.get('tags')"""
    schema = rs.generate_schema(json.dumps(raw_content))
    module = rm.AnsibleModuleBaseAmazon(schema=schema)
    added_ins = {"module": "1.0.0"}
    documentation = g.generate_documentation(
        module,
        added_ins,
        "",
        Path("tests/cloud/fixtures"),
    )
    assert rm.generate_params(documentation["options"]) == expected_params


def test__format_documentation():
    expected = """r'''
module: logs_log_group
short_description: Create and manage log groups
description:
- Create and manage log groups.
options:
    force:
        default: false
        description:
        - Cancel IN_PROGRESS and PENDING resource requestes.
        - Because you can only perform a single operation on a given resource at a
            time, there might be cases where you need to cancel the current resource
            operation to make the resource available so that another operation may
            be performed on it.
        type: bool
    kms_key_id:
        aliases:
        - KmsKeyId
        description:
        - The Amazon Resource Name (ARN) of the CMK to use when encrypting log data.
        type: str
    log_group_name:
        aliases:
        - LogGroupName
        description:
        - The name of the log group.
        - If you dont specify a name, AWS CloudFormation generates a unique ID for
            the log group.
        type: str
    purge_tags:
        default: true
        description:
        - Remove tags not listed in I(tags).
        type: bool
    retention_in_days:
        aliases:
        - RetentionInDays
        choices:
        - 1
        - 3
        - 5
        - 7
        - 14
        - 30
        - 60
        - 90
        - 120
        - 150
        - 180
        - 365
        - 400
        - 545
        - 731
        - 1827
        - 3653
        description:
        - The number of days to retain the log events in the specified log group.
        - 'Possible values are: C(1), C(3), C(5), C(7), C(14), C(30), C(60), C(90),
            C(120), C(150), C(180), C(365), C(400), C(545), C(731), C(1827), and C(3653).'
        type: int
    state:
        choices:
        - present
        - absent
        - list
        - describe
        - get
        default: present
        description:
        - Goal state for resource.
        - I(state=present) creates the resource if it doesn't exist, or updates to
            the provided state if the resource already exists.
        - I(state=absent) ensures an existing instance is deleted.
        - I(state=list) get all the existing resources.
        - I(state=describe) or I(state=get) retrieves information on an existing resource.
        type: str
    tags:
        aliases:
        - Tags
        - resource_tags
        description:
        - A dict of tags to apply to the resource.
        - To remove all tags set I(tags={}) and I(purge_tags=true).
        type: dict
    wait:
        default: false
        description:
        - Wait for operation to complete before returning.
        type: bool
    wait_timeout:
        default: 320
        description:
        - How many seconds to wait for an operation to complete before timing out.
        type: int
author: Ansible Cloud Team (@ansible-collections)
version_added: 1.0.0
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
- amazon.cloud.boto3
'''"""

    schema = rs.generate_schema(json.dumps(raw_content))
    module = rm.AnsibleModuleBaseAmazon(schema=schema)
    added_ins = {"module": "1.0.0"}
    documentation = g.generate_documentation(
        module,
        added_ins,
        "1.0.0",
        Path("tests/cloud/fixtures"),
    )

    assert rm.format_documentation(documentation) == expected


def test__generate_argument_spec():
    expected_argument_spec = """
argument_spec['log_group_name'] = {'type': 'str', 'aliases': ['LogGroupName']}
argument_spec['kms_key_id'] = {'type': 'str', 'aliases': ['KmsKeyId']}
argument_spec['retention_in_days'] = {'type': 'int', 'choices': [1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], 'aliases': ['RetentionInDays']}
argument_spec['tags'] = {'type': 'dict', 'aliases': ['Tags', 'resource_tags']}
argument_spec['state'] = {'type': 'str', 'choices': ['present', 'absent', 'list', 'describe', 'get'], 'default': 'present'}
argument_spec['wait'] = {'type': 'bool', 'default': False}
argument_spec['wait_timeout'] = {'type': 'int', 'default': 320}
argument_spec['force'] = {'type': 'bool', 'default': False}
argument_spec['purge_tags'] = {'type': 'bool', 'default': True}"""
    schema = rs.generate_schema(json.dumps(raw_content))
    module = rm.AnsibleModuleBaseAmazon(schema=schema)
    added_ins = {"module": "1.0.0"}
    documentation = g.generate_documentation(
        module,
        added_ins,
        "",
        Path("tests/cloud/fixtures"),
    )

    assert rm.generate_argument_spec(documentation["options"]) == expected_argument_spec


def test_AnsibleModuleBaseAmazon():
    schema = rs.generate_schema(json.dumps(raw_content))
    module = rm.AnsibleModuleBaseAmazon(schema=schema)
    assert module.name == "logs_log_group"


def test_AnsibleModuleBaseAmazon_is_trusted():
    schema = rs.generate_schema(json.dumps(raw_content))
    module = rm.AnsibleModuleBaseAmazon(schema=schema)
    assert module.is_trusted(Path("tests/cloud/fixtures"))
    module.name = "something_we_dont_trust"
    assert not module.is_trusted(Path("tests/cloud/fixtures"))
