#!/usr/bin/env python3

from ansible_collections.ansible.content_builder.plugins.plugin_utils.cloud_utils import utils


def test_format_documentaion():
    input_arg = {
        "author": "Ansible Cloud Team (@ansible-collections)",
        "description": [
            "Creates and manages a metric stream.",
        ],
        "extends_documentation_fragment": ["amazon.aws.aws", "amazon.aws.ec2"],
        "module": "cloudwatch_metric_stream",
        "options": {
            "exclude_filters": {
                "description": [
                    "This structure defines the metrics that will be streamed."
                ],
                "elements": "dict",
                "suboptions": {
                    "namespace": {
                        "description": [
                            "Only metrics with Namespace matching this value will be streamed."
                        ],
                        "type": "str",
                    }
                },
                "type": "list",
            },
        },
    }
    output = "r'''\nmodule: cloudwatch_metric_stream\ndescription:\n- Creates and manages a metric stream.\noptions:\n    exclude_filters:\n        description:\n        - This structure defines the metrics that will be streamed.\n        elements: dict\n        suboptions:\n            namespace:\n                description:\n                - Only metrics with Namespace matching this value will be streamed.\n                type: str\n        type: list\nauthor: Ansible Cloud Team (@ansible-collections)\nextends_documentation_fragment:\n- amazon.aws.aws\n- amazon.aws.ec2\n'''"
    assert utils.format_documentation(input_arg) == output


def test_indent():
    input_arg = "\nTest indentation.\n4 space should be added\n"
    output = "    \n    Test indentation.\n    4 space should be added\n    \n"
    assert utils.indent(input_arg, 4) == output


def test_python_type():
    assert utils.python_type("object") == "dict"
    assert utils.python_type("string") == "str"
    assert utils.python_type("array") == "list"
    assert utils.python_type("list") == "list"
    assert utils.python_type("boolean") == "bool"
    assert utils.python_type(["object", "string"]) == "dict"
    assert utils.python_type(["string", "object"]) == "str"
