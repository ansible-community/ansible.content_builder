#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2023 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The action plugin file for generate_cloud_modules
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type


import argparse
import json

import pathlib
import re
import yaml
import copy
from typing import Dict, Iterable, List, DefaultDict, Union, Optional, TypeVar, Type
from ansible.plugins.action import ActionBase
from ansible_collections.ansible.content_builder.plugins.plugin_utils.cloud_utils.content_library_data import content_library_static_ds
from ansible_collections.ansible.content_builder.plugins.plugin_utils.cloud_utils.utils import (
    format_documentation,
    indent,
    UtilsBase,
    jinja2_renderer,
    get_module_added_ins,
    get_module_from_config,
    python_type,
    camel_to_snake,
    ignore_description,
)
# import for amazon.cloud doc generation
from ansible_collections.ansible.content_builder.plugins.plugin_utils.cloud_utils.generator import generate_documentation
# import for vmware.vware_rest runtime.yml generation
from ansible_collections.ansible.content_builder.plugins.plugin_utils.cloud_utils.generator import generate_runtime_yml


# vmware specific
def normalize_parameter_name(name: str):
    # the in-query filter.* parameters are not valid Python variable names.
    # We replace the . with a _ to avoid problem,
    return name.replace("filter.", "filter_")  # < 7.0.2


def ansible_state(operationId: str, default_operationIds: Optional[str] = None) -> str:
    mapping = {
        "update": "present",
        "delete": "absent",
        "create": "present",
    }
    # in this case, we don't want to see 'create' in the
    # "Required with" listi
    if (
        default_operationIds
        and operationId == "update"
        and "create" not in default_operationIds
    ):
        return
    if operationId in mapping:
        return mapping[operationId]
    else:
        return operationId


class_description = TypeVar("class_description", bound="Description")


class Description:
    @classmethod
    def normalize(cls: Type[class_description], string_list: List) -> List:
        if not isinstance(string_list, list):
            raise TypeError

        with_no_line_break = []
        for l in string_list:
            if "\n" in l:
                with_no_line_break += l.split("\n")
            else:
                with_no_line_break.append(l)

        with_no_line_break = [cls.write_M(i) for i in with_no_line_break]
        with_no_line_break = [cls.write_I(i) for i in with_no_line_break]
        with_no_line_break = [cls.clean_up(i) for i in with_no_line_break]
        return with_no_line_break

    @classmethod
    def clean_up(cls: Type[class_description], my_string: str) -> str:
        def rewrite_name(matchobj):
            name = matchobj.group(1)
            snake_name = cls.to_snake(name)
            if snake_name[0] == "#":  # operationId:
                output = f"C({ansible_state(snake_name[1:])})"
            output = f"C({snake_name})"
            return output

        def rewrite_link(matchobj: str) -> str:
            name = matchobj.group(1)
            if "#" in name and name.split("#")[0]:
                output = name.split("#")[1]
            else:
                output = name
            return output

        my_string = my_string.replace(" {@term enumerated type}", "")
        my_string = my_string.replace(" {@term list}", "list")
        my_string = my_string.replace(" {@term operation}", "operation")
        my_string = re.sub(r"{@name DayOfWeek}", "day of the week", my_string)
        my_string = re.sub(r": The\s\S+\senumerated type", ": This option", my_string)
        my_string = re.sub(r" <p> ", " ", my_string)
        my_string = re.sub(r" See {@.*}.", "", my_string)
        my_string = re.sub(r"\({@.*?\)", "", my_string)
        my_string = re.sub(r"{@code true}", "C(True)", my_string)
        my_string = re.sub(r"{@code false}", "C(False)", my_string)
        my_string = re.sub(r"{@code\s+?(.*?)}", r"C(\1)", my_string)
        my_string = re.sub(r"{@param.name\s+?([^}]*)}", rewrite_name, my_string)
        my_string = re.sub(r"{@name\s+?([^}]*)}", rewrite_name, my_string)
        # NOTE: it's pretty much impossible to build something useful
        # automatically.
        # my_string = re.sub(r"{@link\s+?([^}]*)}", rewrite_link, my_string)
        for k in content_library_static_ds:
            my_string = re.sub(k, content_library_static_ds[k], my_string)
        return my_string

    @classmethod
    def to_snake(cls: Type[class_description], camel_case: str) -> str:
        camel_case = camel_case.replace("DNS", "dns")
        return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_case).lower()

    @classmethod
    def ref_to_parameter(cls: Type[class_description], ref: str) -> str:
        splitted = ref.split(".")
        my_parameter = splitted[-1].replace("-", "_")
        return cls.to_snake(my_parameter)

    @classmethod
    def write_I(cls: Type[class_description], my_string: str) -> str:
        refs = {
            cls.ref_to_parameter(i): i
            for i in re.findall(r"[A-Z][\w+]+\.[A-Z][\w+\.-]+", my_string)
        }
        for parameter_name in sorted(refs.keys(), key=len, reverse=True):
            ref = refs[parameter_name]
            my_string = my_string.replace(ref, f"I({parameter_name})")
        return my_string

    @classmethod
    def write_M(cls: Type[class_description], my_string: str) -> str:
        my_string = re.sub(r"When operations return.*\.($|\s)", "", my_string)
        m = re.search(r"resource type:\s([a-zA-Z][\w\.]+[a-z])", my_string)
        mapping = {
            "ClusterComputeResource": "vcenter_cluster_info",
            "Datacenter": "vcenter_datacenter_info",
            "Datastore": "vcenter_datastore_info",
            "Folder": "vcenter_folder_info",
            "HostSystem": "vcenter_host_info",
            "Network": "vcenter_network_info",
            "ResourcePool": "vcenter_resourcepool_info",
            "vcenter.StoragePolicy": "vcenter_storage_policies_info",
            "vcenter.vm.hardware.Cdrom": "vcenter_vm_hardware_cdrom",
            "vcenter.vm.hardware.Disk": "vcenter_vm_hardware_disk",
            "vcenter.vm.hardware.Ethernet": "vcenter_vm_hardware_ethernet",
            "vcenter.vm.hardware.Floppy": "vcenter_vm_hardware_floppy",
            "vcenter.vm.hardware.ParallelPort": "vcenter_vm_hardware_parallel",
            "vcenter.vm.hardware.SataAdapter": "vcenter_vm_hardware_adapter_sata",
            "vcenter.vm.hardware.ScsiAdapter": "vcenter_vm_hardware_adapter_scsi",
            "vcenter.vm.hardware.SerialPort": "vcenter_vm_hardware_serial",
            "VirtualMachine": "vcenter_vm_info",
            "infraprofile.profile": "appliance_infraprofile_configs",
            "appliance.vmon.Service": "appliance_vmon_service",
            "appliance.monitoring": "appliance_monitoring_info",
            "appliance.networking.interfaces": "appliance_networking_interfaces_info",
            "appliance.services": "appliance_services_info",
            "StorageProfile": "vcenter_storage_policies_info",
            "spbm.StorageProfile": "vcenter_storage_policies_info",
            "content.library.Item": "content_library_item_info",
            "content.Library": "content_library_info",
            "vcenter.VCenter": "vcenter_cluster_info",
            "content.library.Subscriptions": "content_library_subscriptions_info",
        }

        if not m:
            return my_string

        resource_name = m.group(1)
        try:
            module_name = mapping[resource_name]
        except KeyError:
            print(f"No mapping for {resource_name}")
            raise

        if f"must be an identifier for the resource type: {resource_name}" in my_string:
            return my_string.replace(
                f"must be an identifier for the resource type: {resource_name}",
                f"must be the id of a resource returned by M(vmware.vmware_rest.{module_name})",
            )
        if f"identifiers for the resource type: {resource_name}" in my_string:
            return my_string.replace(
                f"identifiers for the resource type: {resource_name}",
                f"the id of resources returned by M(vmware.vmware_rest.{module_name})",
            ).rstrip()


def gen_documentation(
    name: str,
    description: str,
    parameters: List,
    added_ins: Dict,
    next_version: str,
    target_dir: str,
) -> Dict:

    short_description = description.split(". ")[0]
    documentation = {
        "author": ["Ansible Cloud Team (@ansible-collections)"],
        "description": description,
        "module": name,
        "notes": ["Tested on vSphere 7.0.3"],
        "options": {
            "vcenter_hostname": {
                "description": [
                    "The hostname or IP address of the vSphere vCenter",
                    "If the value is not specified in the task, the value of environment variable C(VMWARE_HOST) will be used instead.",
                ],
                "type": "str",
                "required": True,
            },
            "vcenter_username": {
                "description": [
                    "The vSphere vCenter username",
                    "If the value is not specified in the task, the value of environment variable C(VMWARE_USER) will be used instead.",
                ],
                "type": "str",
                "required": True,
            },
            "vcenter_password": {
                "description": [
                    "The vSphere vCenter password",
                    "If the value is not specified in the task, the value of environment variable C(VMWARE_PASSWORD) will be used instead.",
                ],
                "type": "str",
                "required": True,
            },
            "vcenter_validate_certs": {
                "description": [
                    "Allows connection when SSL certificates are not valid. Set to C(false) when certificates are not trusted.",
                    "If the value is not specified in the task, the value of environment variable C(VMWARE_VALIDATE_CERTS) will be used instead.",
                ],
                "type": "bool",
                "default": True,
            },
            "vcenter_rest_log_file": {
                "description": [
                    "You can use this optional parameter to set the location of a log file. ",
                    "This file will be used to record the HTTP REST interaction. ",
                    "The file will be stored on the host that run the module. ",
                    "If the value is not specified in the task, the value of ",
                    "environment variable C(VMWARE_REST_LOG_FILE) will be used instead.",
                ],
                "type": "str",
            },
            "session_timeout": {
                "description": [
                    "Timeout settings for client session. ",
                    "The maximal number of seconds for the whole operation including connection establishment, request sending and response. ",
                    "The default value is 300s.",
                ],
                "type": "float",
                "version_added": "2.1.0",
            },
        },
        "requirements": ["vSphere 7.0.3 or greater", "python >= 3.6", "aiohttp"],
        "short_description": short_description,
        "version_added": next_version,
    }

    # Note: this series of if block is overcomplicated and should
    # be refactorized.
    for parameter in parameters:
        if parameter["name"] == "action":
            continue
        normalized_name = normalize_parameter_name(parameter["name"])
        description = []
        option = {}
        if parameter.get("required"):
            option["required"] = True
        if parameter.get("aliases"):
            option["aliases"] = parameter.get("aliases")
        if parameter.get("description"):
            description.append(parameter["description"])
        if parameter.get("subkeys"):
            description.append("Valid attributes are:")
            for sub_k, sub_v in parameter.get("subkeys").items():
                sub_v["type"] = python_type(sub_v["type"])
                states = sorted(set([ansible_state(o) for o in sub_v["_operationIds"]]))
                required_with_operations = sorted(
                    set([ansible_state(o) for o in sub_v["_required_with_operations"]])
                )
                description.append(
                    " - C({name}) ({type}): {description} ({states})".format(
                        **sub_v, states=states
                    )
                )
                if required_with_operations:
                    description.append(
                        f"   This key is required with {required_with_operations}."
                    )
                if "enum" in sub_v:
                    description.append("   - Accepted values:")
                    for i in sorted(sub_v["enum"]):
                        description.append(f"     - {i}")
                if "properties" in sub_v:
                    description.append("   - Accepted keys:")
                    for i, v in sub_v["properties"].items():
                        description.append(
                            f"     - {i} ({v['type']}): {v['description']}"
                        )
                        if v.get("enum"):
                            description.append("Accepted value for this field:")
                            for val in sorted(v.get("enum")):
                                description.append(f"       - C({val})")

        option["description"] = list(Description.normalize(description))
        option["type"] = python_type(parameter["type"])
        if "enum" in parameter:
            option["choices"] = sorted(parameter["enum"])
        if parameter["type"] == "array":
            option["elements"] = python_type(parameter["elements"])
        if parameter.get("default"):
            option["default"] = parameter.get("default")

        documentation["options"][normalized_name] = option
        parameter["added_in"] = next_version

    module_from_config = get_module_from_config(name, target_dir)
    if module_from_config and "documentation" in module_from_config:
        for k, v in module_from_config["documentation"].items():
            documentation[k] = v
    return documentation


def path_to_name(path: str) -> str:
    _path = path.lstrip("/").split("?")[0]
    elements = []
    keys = []
    for i in _path.split("/"):
        if "{" in i:
            keys.append(i)
        elif len(keys) > 1:
            # action for a submodule, we gather these end-points in the main module
            continue
        else:
            elements.append(i)

    # workaround for vcenter_vm_power and appliance_services, appliance_shutdown, appliance_system_storage
    if elements[-1] in (
        "stop",
        "start",
        "restart",
        "suspend",
        "reset",
        "cancel",
        "poweroff",
        "reboot",
        "resize",
    ):
        elements = elements[:-1]
    if elements[0:3] == ["rest", "com", "vmware"]:
        elements = elements[3:]
    elif elements[0:2] == ["rest", "hvc"]:
        elements = elements[1:]
    elif elements[0:2] == ["rest", "appliance"]:
        elements = elements[1:]
    elif elements[0:2] == ["rest", "vcenter"]:
        elements = elements[1:]
    elif elements[0:2] == ["rest", "api"]:
        elements = elements[2:]
    elif elements[:1] == ["api"]:
        elements = elements[1:]

    module_name = "_".join(elements)
    return module_name.replace("-", "")


def gen_arguments_py(parameters: List, list_index=None) -> str:
    result = ""
    for parameter in parameters:
        name = normalize_parameter_name(parameter["name"])
        values = []

        if name in ["user_name", "username", "encryption_key", "client_token"]:
            values.append("'no_log': True")
        elif "password" in name:
            values.append("'no_log': True")

        if parameter.get("required"):
            values.append("'required': True")

        aliases = parameter.get("aliases")
        if aliases:
            values.append(f"'aliases': {aliases}")

        _type = python_type(parameter["type"])
        values.append(f"'type': '{_type}'")
        if "enum" in parameter:
            choices = ", ".join([f"'{i}'" for i in sorted(parameter["enum"])])
            values.append(f"'choices': [{choices}]")
        if python_type(parameter["type"]) == "list":
            _elements = python_type(parameter["elements"])
            values.append(f"'elements': '{_elements}'")

        # "bus" option defaulting on 0
        if name == "bus":
            values.append("'default': 0")
        elif "default" in parameter:
            default = parameter["default"]
            values.append(f"'default': '{default}'")

        result += f"\nargument_spec['{name}'] = "
        result += "{" + ", ".join(values) + "}"
    return result


def flatten_ref(tree: any, definitions: Iterable) -> any:
    if isinstance(tree, str):
        if tree.startswith("#/definitions/"):
            raise Exception("TODO")
        return definitions.get(tree)
    if isinstance(tree, list):
        return [flatten_ref(i, definitions) for i in tree]
    if tree is None:
        return {}
    for k in tree:
        v = tree[k]
        if k == "$ref":
            dotted = v.split("/")[2]
            if dotted in ["vapi.std.localization_param", "VapiStdLocalizationParam"]:
                # to avoid an endless loop with
                # vapi.std.nested_localizable_message
                return {"go_to": "vapi.std.localization_param"}
            definition = definitions.get(dotted)
            data = flatten_ref(definition, definitions)
            if "description" not in data and "description" in tree:
                data["description"] = tree["description"]
            return data
        elif isinstance(v, dict):
            tree[k] = flatten_ref(v, definitions)
        else:
            pass
    return tree


class Resource:
    def __init__(self, name: str):
        self.name = name
        self.operations = {}
        self.summary = {}


# amazon.cloud specific
def generate_params(definitions: Iterable) -> str:
    params: str = ""
    keys = sorted(
        definitions.keys() - ["wait", "wait_timeout", "state", "purge_tags", "force"]
    )
    for key in keys:
        params += f"\nparams['{key}'] = module.params.get('{key}')"

    return params


def gen_mutually_exclusive(schema: Dict) -> List:
    primary_idenfifier = schema.get("primaryIdentifier", [])
    entries: List = []

    if len(primary_idenfifier) > 1:
        entries.append([tuple(primary_idenfifier), "identifier"])

    return entries


def ensure_all_identifiers_defined(schema: Dict) -> str:
    primary_idenfifier = schema.get("primaryIdentifier", [])
    new_content: str = "if state in ('present', 'absent', 'get', 'describe') and module.params.get('identifier') is None:\n"
    new_content += 8 * " "
    new_content += f"if not module.params.get('{primary_idenfifier[0]}')" + " ".join(
        map(lambda x: f" or not module.params.get('{x}')", primary_idenfifier[1:])
    )
    new_content += ":\n" + 12 * " "
    new_content += (
        "module.fail_json(f'You must specify both {*identifier, } identifiers.')\n"
    )

    return new_content


def generate_argument_spec(options: Dict) -> str:
    argument_spec: str = ""
    options_copy = copy.deepcopy(options)

    for key in options_copy.keys():
        ignore_description(options_copy[key])

    for key in options_copy.keys():
        argument_spec += f"\nargument_spec['{key}'] = "
        argument_spec += str(options_copy[key])

    argument_spec = argument_spec.replace("suboptions", "options")

    return argument_spec


# common procs
def gen_required_if(schema: Union[List, Dict]) -> List:
    if isinstance(schema, dict):
        primary_idenfifier = schema.get("primaryIdentifier", [])
        required = schema.get("required", [])
        entries: List = []
        states = ["absent", "get"]

        _primary_idenfifier = copy.copy(primary_idenfifier)

        # For compound primary identifiers consisting of multiple resource properties strung together,
        # use the property values in the order that they are specified in the primary identifier definition
        if len(primary_idenfifier) > 1:
            entries.append(["state", "list", primary_idenfifier[:-1], True])
            _primary_idenfifier.append("identifier")

        entries.append(
            [
                "state",
                "present",
                list(set([*_primary_idenfifier, *required])),
                True,
            ]
        )
        [
            entries.append(["state", state, _primary_idenfifier, True])
            for state in states
        ]
    else:
        by_states = DefaultDict(list)
        for parameter in schema:
            for operation in parameter.get("_required_with_operations", []):
                by_states[ansible_state(operation)].append(parameter["name"])
        entries = []
        for operation, fields in by_states.items():
            state = ansible_state(operation)
            if "state" in entries:
                entries.append(["state", state, sorted(set(fields)), True])

    return entries


# Classes
class AnsibleModuleBaseAmazon(UtilsBase):
    template_file = "default_module.j2"

    def __init__(self, schema: Iterable):
        self.schema = schema
        self.name = self.generate_module_name()

    def generate_module_name(self) -> str:
        splitted = self.schema.get("typeName").split("::")
        prefix = splitted[1].lower()
        list_to_str = "".join(map(str, splitted[2:]))
        return prefix + "_" + camel_to_snake(list_to_str)

    def renderer(self, target_dir: str, module_dir: str, next_version: str, role_path: str):
        added_ins = get_module_added_ins(self.name, git_dir=pathlib.Path(target_dir + "/.git"))
        documentation = generate_documentation(
            self,
            added_ins,
            next_version,
            module_dir,
        )

        arguments = generate_argument_spec(documentation["options"])
        documentation_to_string = format_documentation(documentation)

        content = jinja2_renderer(
            self.template_file,
            role_path,
            "amazon_cloud",
            arguments=indent(arguments, 4),
            documentation=documentation_to_string,
            name=self.name,
            resource_type=f"'{self.schema.get('typeName')}'",
            params=indent(generate_params(documentation["options"]), 4),
            primary_identifier=self.schema["primaryIdentifier"],
            required_if=gen_required_if(self.schema),
            mutually_exclusive=gen_mutually_exclusive(self.schema),
            ensure_all_identifiers_defined=ensure_all_identifiers_defined(self.schema)
            if len(self.schema["primaryIdentifier"]) > 1
            else "",
            create_only_properties=self.schema.get("createOnlyProperties", {}),
            handlers=list(self.schema.get("handlers", {}).keys()),
        )

        self.write_module(target_dir, content)


class AnsibleModuleBaseVmware(UtilsBase):
    template_file = "default_module.j2"

    def __init__(self, resource: str, definitions: any):
        self.resource = resource
        self.definitions = definitions
        self.name = resource.name
        self.next_version = "1.0.0"
        self.default_operationIds = set(list(self.resource.operations.keys())) - set(
            ["get", "list"]
        )

    def description(self) -> str:
        prefered_operationId = ["get", "list", "create", "get", "set"]
        for operationId in prefered_operationId:
            if operationId not in self.default_operationIds:
                continue
            if operationId in self.resource.summary:
                return self.resource.summary[operationId].split("\n")[0]

        for operationId in sorted(self.default_operationIds):
            if operationId in self.resource.summary:
                return self.resource.summary[operationId].split("\n")[0]

        print(f"generic description: {self.name}")
        return f"Handle resource of type {self.name}"

    def get_path(self) -> str:
        return list(self.resource.operations.values())[0][1]

    def list_index(self) -> any:
        for i in ["get", "update", "delete"]:
            if i not in self.resource.operations:
                continue
            path = self.resource.operations[i][1]
            break
        else:
            return

        m = re.search(r"{([-\w]+)}$", path)
        if m:
            return m.group(1)

    def payload(self) -> Dict:
        """ "Return a structure that describe the format of the data to send back."""
        payload = {}
        # for operationId in self.resource.operations:
        for operationId in self.default_operationIds:
            if operationId not in self.resource.operations:
                continue
            payload[operationId] = {"query": {}, "body": {}, "path": {}}
            payload_info = {}
            for parameter in AnsibleModuleBaseVmware._property_to_parameter(
                self.resource.operations[operationId][2], self.definitions, operationId
            ):
                _in = parameter["in"] or "body"

                payload_info = parameter["_loc_in_payload"]
                payload[operationId][_in][parameter["name"]] = payload_info
        return payload

    def answer(self) -> any:
        # This is arguably not super elegant. The list outputs just include a summary of the resources,
        # with this little transformation, we get access to the full item
        output_format = None
        for i in ["list", "get"]:
            if i in self.resource.operations:
                output_format = self.resource.operations[i][3]["200"]
        if not output_format:
            return

        if "items" in output_format["schema"]:
            ref = (
                output_format["schema"]["items"]
                .get("$ref", "")
                .replace("Summary", "Info")
            )
        elif "schema" in output_format:
            ref = output_format["schema"].get("$ref")
        else:
            ref = output_format.get("$ref")

        if not ref:
            return
        try:
            raw_answer = flatten_ref({"$ref": ref}, self.definitions)
        except KeyError:
            return
        if "properties" in raw_answer:
            return raw_answer["properties"].keys()

    def parameters(self) -> Iterable:
        def sort_operationsid(input: Iterable) -> Iterable:
            output = sorted(input)
            if "create" in output:
                output = ["create"] + output
            return output

        results = {}
        for operationId in sort_operationsid(self.default_operationIds):
            if operationId not in self.resource.operations:
                continue

            for parameter in AnsibleModuleBaseVmware._property_to_parameter(
                self.resource.operations[operationId][2], self.definitions, operationId
            ):
                name = parameter["name"]
                if name not in results:
                    results[name] = parameter
                    results[name]["operationIds"] = []
                    results[name]["_required_with_operations"] = []

                # Merging two parameters, for instance "action" in
                # /rest/vcenter/vm-template/library-items/{template_library_item}/check-outs
                # and
                # /rest/vcenter/vm-template/library-items/{template_library_item}/check-outs/{vm}
                if "description" not in parameter:
                    pass
                elif "description" not in results[name]:
                    results[name]["description"] = parameter.get("description")
                elif results[name]["description"] != parameter.get("description"):
                    # We can hardly merge two description strings and
                    # get magically something meaningful
                    if len(parameter["description"]) > len(
                        results[name]["description"]
                    ):
                        results[name]["description"] = parameter["description"]
                if "enum" in parameter:
                    results[name]["enum"] += parameter["enum"]
                    results[name]["enum"] = sorted(set(results[name]["enum"]))

                results[name]["operationIds"].append(operationId)
                results[name]["operationIds"].sort()
                if "subkeys" in parameter:
                    if "subkeys" not in results[name]:
                        results[name]["subkeys"] = {}
                    for sub_k, sub_v in parameter["subkeys"].items():
                        if sub_k in results[name]["subkeys"]:
                            results[name]["subkeys"][sub_k][
                                "_required_with_operations"
                            ] += sub_v["_required_with_operations"]
                            results[name]["subkeys"][sub_k]["_operationIds"] += sub_v[
                                "_operationIds"
                            ]
                            results[name]["subkeys"][sub_k]["description"] = sub_v[
                                "description"
                            ]
                        else:
                            results[name]["subkeys"][sub_k] = sub_v

                if parameter.get("required"):
                    results[name]["_required_with_operations"].append(operationId)

        answer_fields = self.answer()
        # Note: If the final result comes with a "label" field, we expose a "label"
        # parameter. We will use the field to identify an existing resource.
        if answer_fields and "label" in answer_fields:
            results["label"] = {
                "type": "str",
                "name": "label",
                "description": "The name of the item",
            }

        for name, result in results.items():
            if result.get("enum"):
                result["enum"] = sorted(set(result["enum"]))
            if result.get("required"):
                if (
                    len(set(self.default_operationIds) - set(result["operationIds"]))
                    > 0
                ):

                    required_with = []
                    for i in result["operationIds"]:
                        state = ansible_state(i, self.default_operationIds)
                        if state:
                            required_with.append(state)
                    result["description"] += " Required with I(state={})".format(
                        sorted(set(required_with))
                    )
                    del result["required"]
                else:
                    result["description"] += " This parameter is mandatory."

        states = []
        for operation in sorted(list(self.default_operationIds)):
            if operation in ["create", "update"]:
                states.append("present")
            elif operation == "delete":
                states.append("absent")
            else:
                states.append(operation)

        results["state"] = {
            "name": "state",
            "type": "str",
            "enum": sorted(set(states)),
        }
        if "present" in states:
            results["state"]["default"] = "present"
        elif "set" in states:
            results["state"]["default"] = "set"
        elif states:
            results["state"]["required"] = True

        # There is just one possible operation, we remove the "state" parameter
        if len(self.resource.operations) == 1:
            del results["state"]

        # Suppport pre 7.0.2 filters
        if "list" in self.default_operationIds or "get" in self.default_operationIds:
            for i in ["datacenters", "folders", "names"]:
                if i in results and results[i]["type"] == "array":
                    results[i]["aliases"] = [f"filter_{i}"]
            if "type" in results and results["type"]["type"] == "string":
                results["type"]["aliases"] = ["filter_type"]
            if "types" in results and results["types"]["type"] == "array":
                results["types"]["aliases"] = ["filter_types"]

        return sorted(results.values(), key=lambda item: item["name"])

    def gen_required_if(self, parameters: List) -> List:
        by_states = DefaultDict(list)
        for parameter in parameters:
            for operation in parameter.get("_required_with_operations", []):
                by_states[ansible_state(operation)].append(parameter["name"])
        entries = []
        for operation, fields in by_states.items():
            state = ansible_state(operation)
            if "state" in entries:
                entries.append(["state", state, sorted(set(fields)), True])
        return entries

    @staticmethod
    def _property_to_parameter(
        prop_struct: any, definitions: Iterable, operationId: any
    ) -> Iterable:
        properties = flatten_ref(prop_struct, definitions)

        def get_next(properties: List) -> Iterable:
            required_keys = []
            for i, v in enumerate(properties):
                if "schema" in v:
                    if "properties" in v["schema"]:
                        properties[i] = v["schema"]["properties"]
                        if "required" in v["schema"]:
                            required_keys = v["schema"]["required"]
                    elif "additionalProperties" in v["schema"]:
                        properties[i] = v["schema"]["additionalProperties"][
                            "properties"
                        ]

            for i, v in enumerate(properties):
                # appliance_health_messages
                if isinstance(v, str):
                    yield v, {}, [], []

                elif "spec" in v and "properties" in v["spec"]:
                    required_keys = required_keys or []
                    if "required" in v["spec"]:
                        required_keys = v["spec"]["required"]
                    for name, property in v["spec"]["properties"].items():
                        yield name, property, ["spec"], name in required_keys

                elif isinstance(v, dict):
                    if not isinstance(v, dict):
                        continue
                    # {'type': 'string', 'required': True, 'in': 'path', 'name': 'datacenter', 'description': 'Identifier of the datacenter.'}
                    if "name" in v and "in" in v and v.get("in") in ["path", "query"]:
                        yield v["name"], v, [], v.get("required")
                    # elif "name" in v and isinstance(v["name", dict]):
                    #    yield v["name"], v, [], v.get("required")
                    else:
                        for k, data in v.items():
                            if isinstance(data, dict):
                                yield k, data, [], k in required_keys or data.get(
                                    "required"
                                )

        parameters = []

        for name, v, parent, required in get_next(properties):
            if name == "request_body":
                raise ValueError()
            parameter = {
                "name": name,
                "type": v.get("type", "str"),  # 'str' by default, should be ok
                "description": v.get("description", ""),
                "required": required,
                "_loc_in_payload": "/".join(parent + [name]),
                "in": v.get("in"),
            }
            if "enum" in v:
                parameter["enum"] = sorted(set(v["enum"]))

            sub_items = None
            required_subkeys = v.get("required", [])

            if "properties" in v:
                sub_items = v["properties"]
                if "required" in v["properties"]:  # NOTE: do we still need these
                    required_subkeys = v["properties"]["required"]
            elif "items" in v and "properties" in v["items"]:
                sub_items = v["items"]["properties"]
                if "required" in v["items"]:  # NOTE: do we still need these
                    required_subkeys = v["items"]["required"]
            elif "items" in v and "name" not in v["items"]:
                parameter["elements"] = v["items"].get("type", "str")
            elif "items" in v and v["items"]["name"]:
                sub_items = v["items"]

            if sub_items:
                subkeys = {}
                for sub_k, sub_v in sub_items.items():
                    subkey = {
                        "name": sub_k,
                        "type": sub_v["type"],
                        "description": sub_v.get("description", ""),
                        "_required_with_operations": [operationId]
                        if sub_k in required_subkeys
                        else [],
                        "_operationIds": [operationId],
                    }
                    if "enum" in sub_v:
                        subkey["enum"] = sub_v["enum"]
                    if "properties" in sub_v:
                        subkey["properties"] = sub_v["properties"]
                    subkeys[sub_k] = subkey
                parameter["subkeys"] = subkeys
                parameter["elements"] = "dict"
            parameters.append(parameter)

        return sorted(
            parameters, key=lambda item: (item["name"], item.get("description"))
        )

    def list_path(self) -> any:
        list_path = None
        if "list" in self.resource.operations:
            list_path = self.resource.operations["list"][1]

        return list_path

    def renderer(self, target_dir: str, module_dir: str, role_path: str):

        added_ins = {}  # get_module_added_ins(self.name, git_dir=target_dir / ".git")
        arguments = gen_arguments_py(self.parameters(), self.list_index())
        documentation = format_documentation(
            gen_documentation(
                self.name,
                self.description(),
                self.parameters(),
                added_ins,
                self.next_version,
                module_dir,
            )
        )
        required_if = gen_required_if(self.parameters())

        content = jinja2_renderer(
            self.template_file,
            role_path,
            "vmware_rest",
            arguments=indent(arguments, 4),
            documentation=documentation,
            list_index=self.list_index(),
            list_path=self.list_path(),
            name=self.name,
            operations=self.resource.operations,
            path=self.get_path(),
            payload_format=self.payload(),
            required_if=required_if,
        )

        self.write_module(target_dir, content)


class AnsibleInfoModule(AnsibleModuleBaseVmware):
    def __init__(self, resource: any, definitions: any):
        super().__init__(resource, definitions)
        self.name = resource.name + "_info"
        self.default_operationIds = ["get", "list"]

    def parameters(self) -> List:
        return [i for i in list(super().parameters()) if i["name"] != "state"]


class AnsibleInfoNoListModule(AnsibleInfoModule):
    template_file = "info_no_list_module.j2"


class AnsibleInfoListOnlyModule(AnsibleInfoModule):
    template_file = "info_list_and_get_module.j2"


class Definitions:
    def __init__(self, data: any):
        super().__init__()
        self.definitions = data

    def get(self, ref: any) -> any:
        if isinstance(ref, dict):
            # TODO: standardize the input to avoid this step
            dotted = ref["$ref"].split("/")[2]
        else:
            dotted = ref

        try:
            definition = self.definitions[dotted]
        except KeyError:
            definition = self.definitions["com.vmware." + dotted]

        if definition is None:
            raise Exception("Cannot find ref for {ref}")

        return definition


class Path:
    def __init__(self, path: str, value: any):
        super().__init__()
        self.path = path
        self.operations = {}
        self.verb = {}
        self.value = value

    def summary(self, verb: str) -> str:
        return self.value[verb]["summary"]

    def is_tech_preview(self) -> bool:
        for verb in self.value.keys():
            if "Technology Preview" in self.summary(verb):
                return True
        return False


class SwaggerFile:
    def __init__(self, raw_content: any):
        super().__init__()
        self.resources = {}
        json_content = json.loads(raw_content)
        self.definitions = Definitions(json_content["definitions"])
        self.paths = self.load_paths(json_content["paths"])

    @staticmethod
    def load_paths(paths: str) -> Dict:
        result = {}

        for path in [Path(p, v) for p, v in paths.items()]:
            if path.is_tech_preview():
                continue
            result[path.path] = path
            for verb, desc in path.value.items():
                operationId = desc["operationId"]
                if desc.get("deprecated"):
                    continue
                try:
                    parameters = desc["parameters"]
                except KeyError:
                    print(f"No parameters for {operationId} {path.path}")
                if path.path.startswith("/rest/vcenter/vm/{vm}/tools"):
                    if operationId == "upgrade":
                        print(f"Skipping {path.path} upgrade (broken)")
                        continue
                if path.path == "/api/appliance/infraprofile/configs":
                    if operationId == "validate$task":
                        print(f"Skipping {path.path} upgrade (broken)")
                        continue
                path.operations[operationId] = (
                    verb,
                    path.path,
                    parameters,
                    desc["responses"],
                )
        return result

    @staticmethod
    def init_resources(paths: str) -> Dict:
        resources = {}
        for path in paths:
            if "vmw-task=true" in path.path:
                continue

            name = path_to_name(path.path)
            if name == "esx_settings_clusters_software_drafts":
                continue
            if name not in resources:
                resources[name] = Resource(name)

            for operationId, v in path.operations.items():
                verb = v[0]
                resources[name].summary[operationId] = path.summary(verb)
                if operationId in resources[name].operations:
                    print(
                        f"Cannot create operationId ({operationId}) with path "
                        f"({verb}) {path.path}. already defined: "
                        f"{resources[name].operations[operationId]}"
                    )
                    continue
                operationId = operationId.replace(
                    "$task", ""
                )  # NOTE: Not sure if this is the right thing to do
                resources[name].operations[operationId] = v
        return resources


# module_generation procs


def generate_amazon_cloud(args: Iterable, role_path: str):
    module_list = []
    resource_file = pathlib.Path(args.get("modules") + "/modules.yaml")

    RESOURCES = yaml.load(
        pathlib.Path(resource_file).read_text(), Loader=yaml.FullLoader
    )

    for module in RESOURCES:
        for k, v in module.items():
            type_name = v["resource"]
        file_name = re.sub("::", "_", type_name)
        print(f"Generating modules {file_name}")
        schema_file = pathlib.Path(args.get("schema_dir") + "/" + file_name + ".json")
        schema = json.loads(schema_file.read_text())

        module = AnsibleModuleBaseAmazon(schema=schema)

        if module.is_trusted(args.get("modules")):
            module.renderer(
                target_dir=args.get("target_dir"),
                module_dir=args.get("modules"),
                next_version=args.get("next_version"),
                role_path=role_path,
            )
            module_list.append(module.name)

    modules = [f"plugins/modules/{module}.py" for module in module_list]
    module_utils = ["plugins/module_utils/core.py", "plugins/module_utils/utils.py"]

    ignore_dir = pathlib.Path(args.get("target_dir") + "/tests/sanity")
    ignore_dir.mkdir(parents=True, exist_ok=True)

    for version in ["2.9", "2.10", "2.11", "2.12", "2.13", "2.14", "2.15"]:
        per_version_ignore_content = ""
        skip_list = []

        if version in ["2.9", "2.10", "2.11"]:
            skip_list += [
                "compile-2.7!skip",  # Py3.6+
                "compile-3.5!skip",  # Py3.6+
                "import-2.7!skip",  # Py3.6+
                "import-3.5!skip",  # Py3.6+
                "future-import-boilerplate!skip",  # Py2 only
                "metaclass-boilerplate!skip",  # Py2 only
                "compile-2.6!skip",  # Py3.6+
                "import-2.6!skip",  # Py3.6+
            ]
        validate_skip_needed = [
            "plugins/modules/s3_bucket.py",
            "plugins/modules/backup_backup_vault.py",
            "plugins/modules/backup_framework.py",
            "plugins/modules/backup_report_plan.py",
            "plugins/modules/lambda_function.py",
            "plugins/modules/rdsdb_proxy.py",
            "plugins/modules/redshift_cluster.py",
            "plugins/modules/eks_cluster.py",
            "plugins/modules/dynamodb_global_table.py",
            "plugins/modules/kms_replica_key.py",
            "plugins/modules/rds_db_proxy.py",
            "plugins/modules/iam_server_certificate.py",
            "plugins/modules/cloudtrail_trail.py",
            "plugins/modules/route53_key_signing_key.py",
            "plugins/modules/redshift_endpoint_authorization.py",
            "plugins/modules/eks_fargate_profile.py",
            "plugins/modules/autoscaling_launch_configuration.py",
            "plugins/modules/ecr_repository.py",
            "plugins/modules/rds_db_instance.py",
            "plugins/modules/ssm_resource_data_sync.py",
            "plugins/modules/logs_metric_filter.py",
            "plugins/modules/ecs_cluster.py",
        ]
        mutually_exclusive_skip = [
            "plugins/modules/eks_addon.py",
            "plugins/modules/eks_fargate_profile.py",
            "plugins/modules/redshift_endpoint_authorization.py",
            "plugins/modules/route53_key_signing_key.py",
            "plugins/modules/autoscaling_lifecycle_hook.py",
            "plugins/modules/ecs_primary_task_set.py",
            "plugins/modules/logs_metric_filter.py",
            "plugins/modules/wafv2_ip_set.py",
            "plugins/modules/wafv2_regex_pattern_set.py",
            "plugins/modules/wafv2_web_acl_association.py",
        ]

        for f in module_utils:
            for skip in skip_list:
                per_version_ignore_content += f"{f} {skip}\n"

        for f in modules:
            for skip in skip_list:
                per_version_ignore_content += f"{f} {skip}\n"

            if f in validate_skip_needed:
                if version in ["2.10", "2.11", "2.12", "2.13", "2.14"]:
                    if (
                        f == "plugins/modules/redshift_endpoint_authorization.py"
                        and version in ("2.11", "2.12", "2.13", "2.14")
                    ):
                        pass
                    else:
                        validate_skip_list = [
                            "validate-modules:no-log-needed",
                        ]
                        for skip in validate_skip_list:
                            per_version_ignore_content += f"{f} {skip}\n"

            if version in ["2.10", "2.11", "2.12", "2.13", "2.14"]:
                per_version_ignore_content += (
                    f"{f} validate-modules:parameter-state-invalid-choice\n"
                )

        for f in mutually_exclusive_skip:
            per_version_ignore_content += (
                f"{f} validate-modules:mutually_exclusive-type\n"
            )

        ignore_file = ignore_dir / f"ignore-{version}.txt"

        # keep all non-plugins entries from ignore file
        if ignore_file.exists():
            for line in ignore_file.read_text().split("\n"):
                if not line.startswith("plugins/"):
                    per_version_ignore_content += line + "\n"

        ignore_file.write_text(per_version_ignore_content)

    meta_dir = pathlib.Path(args.get("target_dir") + "/meta")
    meta_dir.mkdir(parents=True, exist_ok=True)
    yaml_dict = {
        "requires_ansible": """>=2.11.0""",
        "action_groups": {"aws": []},
        "plugin_routing": {"modules": {}},
    }
    for m in module_list:
        yaml_dict["action_groups"]["aws"].append(m)

    yaml_dict["plugin_routing"]["modules"].update(
        {
            "rdsdb_proxy": {"redirect": "amazon.cloud.rds_db_proxy"},
            "s3_object_lambda_access_point": {
                "redirect": "amazon.cloud.s3objectlambda_access_point"
            },
            "s3_object_lambda_access_point_policy": {
                "redirect": "amazon.cloud.s3objectlambda_access_point_policy"
            },
        }
    )
    yaml_dict["action_groups"]["aws"].extend(
        [
            "rdsdb_proxy",
            "s3_object_lambda_access_point",
            "s3_object_lambda_access_point_policy",
        ]
    )

    runtime_file = meta_dir / "runtime.yml"
    with open(runtime_file, "w") as file:
        yaml.safe_dump(yaml_dict, file, sort_keys=False)

    return


def generate_vmware_rest(args: Iterable, role_path: str):
    module_list = []

    for json_file in ["vcenter.json", "content.json", "appliance.json"]:
        print("Generating modules from {}".format(json_file))
        api_spec_file = pathlib.Path(args.get("schema_dir") + "/" + json_file)
        raw_content = api_spec_file.read_text()
        swagger_file = SwaggerFile(raw_content)
        resources = swagger_file.init_resources(swagger_file.paths.values())

        for resource in resources.values():
            if resource.name == "appliance_logging_forwarding":
                continue
            if resource.name.startswith("vcenter_trustedinfrastructure"):
                continue
            if "list" in resource.operations:
                module = AnsibleInfoListOnlyModule(
                    resource, definitions=swagger_file.definitions
                )
                if (
                    module.is_trusted(args.get("modules"))
                    and len(module.default_operationIds) > 0
                ):
                    module.renderer(
                        target_dir=args.get("target_dir"),
                        module_dir=args.get("modules"),
                        role_path=role_path
                    )
                    module_list.append(module.name)
            elif "get" in resource.operations:
                module = AnsibleInfoNoListModule(
                    resource, definitions=swagger_file.definitions
                )
                if (
                    module.is_trusted(args.get("modules"))
                    and len(module.default_operationIds) > 0
                ):
                    module.renderer(
                        target_dir=args.get("target_dir"),
                        module_dir=args.get("modules"),
                        role_path=role_path,
                    )
                    module_list.append(module.name)

            module = AnsibleModuleBaseVmware(
                resource, definitions=swagger_file.definitions
            )

            if module.is_trusted(args.get("modules")) and len(module.default_operationIds) > 0:
                module.renderer(
                    target_dir=args.get("target_dir"),
                    module_dir=args.get("modules"),
                    role_path=role_path
                )
                module_list.append(module.name)

    print("Generating meta/runtime.yml")
    runtime_yml = generate_runtime_yml(args.get("requires_ansible"), "vmware_rest", module_list)
    meta_dir = pathlib.Path(args.get("target_dir") + "/meta")
    meta_dir.mkdir(parents=True, exist_ok=True)
    runtime_file = meta_dir / "runtime.yml"
    with open(runtime_file, "w") as file:
        yaml.safe_dump(runtime_yml, file, sort_keys=False)

    return


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
        func = "generate_" + args['collection'] + "(args, task_vars['vars']['role_path'])"
        eval(func)

        # info = VersionInfo("content_builder")
        dev_md = pathlib.Path(args.get("target_dir") + "/dev.md")
        dev_md.write_text(
            (
                "The modules are autogenerated by:\n"
                "https://github.com/ansible-community/ansible.content_builder\n"
                ""

            )
        )
        dev_md = pathlib.Path(args.get("target_dir") + "/commit_message")
        dev_md.write_text(
            (
                "bump auto-generated modules\n"
                "\n"
                "The modules are autogenerated by:\n"
                ""
            )
        )
        return self._result
