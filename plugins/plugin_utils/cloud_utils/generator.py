#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import copy
import re
from typing import Iterable, List, Dict
from ansible_collections.ansible.content_builder.plugins.plugin_utils.cloud_utils.utils import (
    python_type,
    get_module_from_config,
    scrub_keys,
    camel_to_snake,
    ensure_description,
)


class Description:
    @classmethod
    def normalize(cls, string: str, definitions: Iterable = {}) -> List[str]:
        with_no_line_break: List[str] = []
        sentences = re.split(r"(?<=[^A-Z].[.?]) +(?=[A-Z])", string)
        sentences[:] = [x for x in sentences if x]

        for line in sentences:
            if "\n" in line:
                splitted = line.split("\n")
                splitted[:] = [x for x in splitted if x]
                with_no_line_break += splitted
            else:
                with_no_line_break.append(line)

        with_no_line_break = [cls.clean_up(definitions, i) for i in with_no_line_break]

        return with_no_line_break

    @classmethod
    def clean_up(cls, definitions: Iterable, my_string: str) -> str:
        values = set()
        keys = set()

        ignored_values = set(["PUT", "S3", "EC2"])

        def get_keys(a_dict):
            keys = []
            if isinstance(a_dict, list):
                for item in a_dict:
                    keys.extend(get_keys(item))
            elif isinstance(a_dict, dict):
                for key in a_dict:
                    keys.append(key)
                    keys.extend(get_keys(a_dict[key]))
            return keys

        def get_values(a_dict):
            for key, value in a_dict.items():
                if isinstance(value, dict):
                    yield from get_values(value)
                else:
                    if key in ("choices", "enum"):
                        yield value

        for value in get_values(definitions):
            values |= set(value)

        keys = set(get_keys(definitions))

        def rewrite_name(matchobj):
            """Rewrite option name to I(camel_to_snake(option))"""
            name = matchobj.group(0)
            if name in keys:
                snake_name = camel_to_snake(name)
                output = f"I({snake_name})"
                return output
            return name

        def rewrite_value(matchobj):
            """Find link and replace it with U(link)"""
            name = matchobj.group(0)
            if name.isalpha():
                if name in values and name not in ignored_values:
                    output = f"C({name})"
                    return output
            else:
                if name not in ignored_values:
                    output = f"C({name})"
                    return output
            return name

        def rewrite_link(matchobj):
            """Find link and replace it with U(link)."""
            name = matchobj.group(0)
            output = f"U({name})"
            return output

        def find_match(pattern, my_string):
            """Find matching string using a pattern and rewrite it as needed."""
            matches = re.findall(pattern, my_string)
            if matches:
                output = re.sub(r"\d+", rewrite_value, my_string)
                output = re.sub(r"(?<!^)(?<!\. )[A-Z][a-z]+", rewrite_name, output)
                return output
            return my_string

        def format_string(line):
            """
            Find CamelCase words (likely to be parameter names, some rewite I(to_snake).
            Find uppercase words (likely to be values like EXAMPLE or EXAMPLE_EXAMPLE and rewrite with C(EXAMPLE)).
            """
            lword = re.sub(r"([A-Z]+[A-Za-z]+)+([A-Z][a-z]+)+", rewrite_name, line)
            lword = re.sub(r"[A-Z_]+[0-9A-Z]+", rewrite_value, lword)
            return lword

        my_string = format_string(my_string)

        # Find link and replace it with U(link)
        my_string = re.sub(r"(https?://[^\s]+)", rewrite_link, my_string)

        # Cleanup phrase removing square brackets contained words
        my_string = re.sub(r"[\[].*?[\]]", "", my_string)

        my_string = find_match("values are:", my_string)
        my_string = find_match("following properties:", my_string)

        # Substitute one or more white space at beginning and end of the string with an empty string
        my_string = re.sub(r"^\s+|\s+$", "", my_string)
        my_string = re.sub(r"TRUE", "C(True)", my_string)

        # Cleanup some quotes
        my_string = re.sub("[\"'\\`]", "", my_string)

        if not my_string.endswith("."):
            my_string = my_string + "."

        return my_string


class Documentation:
    def replace_keys(self, options: Iterable, definitions: Iterable):
        """Sanitize module's options and replace $ref with the correspoding parameters"""
        dict_copy = copy.copy(options)
        for key in dict_copy.keys():
            key_path = f"/properties/{key}"
            if (
                key_path in self.read_only_properties
                and key_path not in self.primary_identifier
            ):
                options.pop(key)
                continue

            item = options[key]

            if isinstance(item, list):
                if key == "enum":
                    options["choices"] = sorted(options.pop(key))
                if key == "type":
                    options[key] = python_type(options[key])
                if key == "oneOf":
                    one_of = options.pop(key)
                    to_be_updated: Dict = {}
                    for elem in one_of:
                        if "required" in elem:
                            elem.pop("required")
                        if "properties" in elem:
                            to_be_updated.update(elem["properties"])
                        else:
                            to_be_updated.update(elem)
                    options["suboptions"] = to_be_updated
                    self.replace_keys(options["suboptions"], definitions)
            elif isinstance(item, dict):
                if key == "properties":
                    options["suboptions"] = options.pop(key)
                    key = "suboptions"

                if "$ref" in item:
                    lookup_param = item["$ref"].split("/")[-1].strip()
                    if definitions.get(lookup_param):
                        result = definitions[lookup_param]
                        item.pop("$ref")
                        if item.get("description") and result.get("description"):
                            if isinstance(item["description"], list):
                                item["description"].extend(result.pop("description"))
                                item["description"] = list(
                                    Description.normalize(
                                        item["description"], self.definitions
                                    )
                                )
                            else:
                                item["description"] += result.pop("description")
                                item["description"] = list(
                                    Description.normalize(
                                        item["description"], self.definitions
                                    )
                                )

                        item.update(result)
                        options[key] = item
                self.replace_keys(options[key], definitions)
            elif isinstance(item, str):
                if key == "type":
                    options[key] = python_type(options[key])
                if key == "description":
                    options[key] = list(
                        Description.normalize(options[key], self.definitions)
                    )
                if key == "const":
                    options["default"] = options.pop(key)

    def cleanup_required(self, a_dict: Iterable):
        a_dict_copy = copy.copy(a_dict)

        if not isinstance(a_dict, dict):
            return a_dict

        for k, v in a_dict_copy.items():
            if isinstance(v, dict):
                if "items" in a_dict[k]:
                    if a_dict[k]["items"].get("type"):
                        a_dict[k]["elements"] = python_type(
                            a_dict_copy[k]["items"].pop("type")
                        )
                    a_dict[k] = dict(a_dict_copy[k], **a_dict[k].pop("items"))
                    v = a_dict[k]

                if "required" in v and isinstance(v["required"], list):
                    a_dict[k].pop("required")

            self.cleanup_required(a_dict[k])

    def cleanup_readonly_properties(self):
        options = copy.deepcopy(self.options)

        def _cleanup_readonly_properties(nested_dict, key_list):
            if not key_list:
                return nested_dict
            key = key_list[0]
            if key in nested_dict:
                if len(key_list) == 1:
                    return nested_dict.pop(key, None)
                else:
                    return _cleanup_readonly_properties(
                        nested_dict[key]["suboptions"], key_list[1:]
                    )
            else:
                return None

        for item in self.read_only_properties:
            opt = item.split("/")
            _cleanup_readonly_properties(options, opt[2:])
            # Remove option entirely if all the suboptions have been removed
            if options.get(opt[2]) and options.pop(opt[2]).get("suboptions", {}) == {}:
                options.pop(opt[2])
        return options

    def preprocess(self) -> Iterable:
        list_of_keys_to_remove = [
            "additionalProperties",
            "insertionOrder",
            "uniqueItems",
            "pattern",
            "examples",
            "maxLength",
            "minLength",
            "format",
            "minimum",
            "maximum",
            "patternProperties",
            "maxItems",
            "minItems",
            "$comment",
            "exclusiveMaximum",
            "exclusiveMinimum",
            "maxProperties",
            "anyOf",
        ]
        self.replace_keys(self.options, self.definitions)
        self.cleanup_required(self.options)
        self.options = self.cleanup_readonly_properties()
        sanitized_options: Iterable = camel_to_snake(
            scrub_keys(self.options, list_of_keys_to_remove)
        )

        """
        For all the options with a missing description field returned by the API
        we make sure to add "description": "Not Provided." to allow
        ansible-doc -t module amazon.cloud.module_name to succeed.

        Without this workaround, sanity tests fail with (even if the ignore files
        are populated with "validate-modules:invalid-documentation"):

        >>> Standard Error
        ERROR! Unable to retrieve documentation from 'amazon.cloud.module_name' due to:
        All (sub-)options and return values must have a 'description' field
        """
        sanitized_options: Iterable = ensure_description(
            sanitized_options, "description"
        )

        return sanitized_options


def generate_documentation(
    module: object, added_ins: Dict, next_version: str, target_dir: str
) -> Iterable:
    """Format and generate the AnsibleModule documentation"""

    module_name = module.name
    documentation: Iterable = {
        "module": module_name,
        "author": "Ansible Cloud Team (@ansible-collections)",
        "description": [],
        "short_description": [],
        "options": {},
        "version_added": added_ins["module"] or next_version,
        "extends_documentation_fragment": [
            "amazon.aws.aws",
            "amazon.aws.ec2",
            "amazon.cloud.boto3",
        ],
    }

    docs = Documentation()
    docs.options = module.schema.get("properties", {})
    docs.definitions = module.schema.get("definitions", {})

    # Properties defined as required must be specified in the desired state during resource creation
    docs.required = module.schema.get("required", [])

    # Properties defined as readOnlyProperties can't be set by users
    docs.read_only_properties = module.schema.get("readOnlyProperties", [])

    docs.primary_identifier = module.schema.get("primaryIdentifier", [])

    # Properties defined as writeOnlyProperties can be specified by users when creating or updating a
    # resource but can't be returned during a read or list requested
    # write_only_properties = module.schema.get("readOnlyProperties")

    documentation["options"] = docs.preprocess()
    documentation["options"].update(
        {
            "state": {
                "description": [
                    "Goal state for resource.",
                    "I(state=present) creates the resource if it doesn't exist, or updates to the provided state if the resource already exists.",
                    "I(state=absent) ensures an existing instance is deleted.",
                    "I(state=list) get all the existing resources.",
                    "I(state=describe) or I(state=get) retrieves information on an existing resource.",
                ],
                "type": "str",
                "choices": ["present", "absent", "list", "describe", "get"],
                "default": "present",
            },
            "wait": {
                "description": ["Wait for operation to complete before returning."],
                "type": "bool",
                "default": False,
            },
            "wait_timeout": {
                "description": [
                    "How many seconds to wait for an operation to complete before timing out.",
                ],
                "type": "int",
                "default": 320,
            },
            "force": {
                "description": [
                    "Cancel IN_PROGRESS and PENDING resource requestes.",
                    "Because you can only perform a single operation on a given resource at a time, there might be cases where you need to cancel the current resource operation to make the resource available so that another operation may be performed on it.",
                ],
                "type": "bool",
                "default": False,
            },
        }
    )

    # module.schema.get("taggable") is not returned always (even if the resource supports tagging)
    if module.schema.get("taggable") or documentation["options"].get("tags"):
        documentation["options"]["tags"] = {
            "description": [
                "A dict of tags to apply to the resource.",
                "To remove all tags set I(tags={}) and I(purge_tags=true).",
            ],
            "type": "dict",
            # The first alias must be the one that will be used for the API calls
            "aliases": ["Tags", "resource_tags"],
        }
        documentation["options"]["purge_tags"] = {
            "description": ["Remove tags not listed in I(tags)."],
            "type": "bool",
            "default": True,
        }

    if len(docs.primary_identifier) > 1:
        # If a resource has more than one primary identifier, the user can decide to either
        # specify all the primary identifiers or use the identifier parameter as a string
        # consisting of the multiple identifiers strung together
        # https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/resource-identifier.html
        documentation["options"]["identifier"] = {
            "description": [
                "For compound primary identifiers, to specify the primary identifier as a string, list each in the order that they are specified in the identifier list definition, separated by '|'.",
                "For more details, visit U(https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/resource-identifier.html).",
            ],
            "type": "str",
        }

    module_from_config = get_module_from_config(module_name, target_dir)
    if module_from_config and "documentation" in module_from_config:
        for k, v in module_from_config["documentation"].items():
            documentation[k] = v

    return documentation


class CloudFormationWrapper:
    """Encapsulates Amazon CloudFormation operations."""

    def __init__(self, client):
        """
        :param client: A Boto3 CloudFormation client
        """
        self.client = client

    def generate_docs(self, type_name: str):
        """
        Equivalent to
        aws cloudformation describe-type \
            --type-name My::Logs::LogGroup \
            --type RESOURCE
        """
        # TODO: include version
        response = self.client.describe_type(Type="RESOURCE", TypeName=type_name)

        return response.get("Schema")
