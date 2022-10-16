from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import re
import sys
import oyaml as yaml
from collections import OrderedDict, deque

from ansible.module_utils.six import iteritems


def generate_documentation(
    json_payload,
    module_name,
    module_version,
    module_resource,
    author,
    temp_data_file,
):
    def doc_option_generator(json_payload, temp_payload):
        for k, v in iteritems(json_payload):
            if isinstance(v, dict):
                for key, val in iteritems(v):
                    if "type" in val and dict(val)["type"] != "array":
                        if val["type"] == "string":
                            temp_payload[key] = {"type": "str"}
                        if val["type"] == "integer":
                            temp_payload[key] = {"type": "int"}
                        if val["type"] == "boolean":
                            temp_payload[key] = {"type": "bool"}
                        if (
                            val.get("description")
                            and temp_payload.get(key)
                            and not temp_payload[key].get("description")
                        ):
                            val_description = re.sub(
                                "`", "'", val["description"]
                            )
                            val_description = re.sub(
                                "'\\n'", "'\\\\n'", val_description
                            )
                            temp = {"description": val_description}
                            temp.update(temp_payload[key])
                            temp_payload[key] = temp
                        if val.get("enum") and not temp_payload[key].get(
                            "choices"
                        ):
                            temp_payload[key].update({"choices": val["enum"]})
                    if (
                        "type" in val
                        and dict(val)["type"] == "array"
                        and "items" in val
                        and "type" in dict(val)["items"]
                    ):
                        temp_payload[key] = {"type": "list"}
                        if val["items"]["type"] == "string":
                            temp_payload[key].update({"elements": "str"})
                        elif val["items"]["type"] == "integer":
                            temp_payload[key].update({"elements": "int"})
                        if val.get("enum"):
                            temp_payload[key].update({"choices": val["enum"]})
                        if val.get("description") and not temp_payload[
                            key
                        ].get("description"):
                            val_description = re.sub(
                                "`", "'", val["description"]
                            )
                            val_description = re.sub(
                                "'\\n'", "'\\\\\\n'", val_description
                            )
                            temp = {"description": val_description}
                            temp.update(temp_payload[key])
                            temp_payload[key] = temp
                        if val.get("enum") and not temp_payload[key].get(
                            "choices"
                        ):
                            temp_payload[key].update({"choices": val["enum"]})
                    elif (
                        "type" in val
                        and dict(val)["type"] == "list"
                        and "suboptions" in val
                        and isinstance(dict(val)["suboptions"], dict)
                    ):
                        if val.get("description") and not temp_payload[
                            key
                        ].get("description"):
                            val_description = re.sub(
                                "`", "'", val["description"]
                            )
                            val_description = re.sub(
                                "'\\n'", "'\\\\n'", val_description
                            )
                            temp = {"description": val_description}
                            temp.update(temp_payload[key])
                            temp_payload[key] = temp
                        if val.get("enum") and not temp_payload[key].get(
                            "choices"
                        ):
                            temp_payload[key].update({"choices": val["enum"]})
                        temp_payload[key] = v[key]
                    elif (
                        "type" in val
                        and dict(val)["type"] == "array"
                        and "element-type" in val
                    ):
                        temp_payload[key] = dict()
                        temp_payload[key]["description"] = val["description"]
                        temp_payload[key]["type"] = "list"
                        if val["element-type"] == "string":
                            temp_payload[key]["elements"] = "str"
                        else:
                            temp_payload[key]["elements"] = val["element-type"]
                    elif (
                        "type" in val
                        and (
                            dict(val)["type"] == "array"
                            or dict(val)["type"] == "dict"
                        )
                        and "suboptions" in val
                        and isinstance(dict(val)["suboptions"], dict)
                    ):
                        print("Under Processing!!")
                        temp_payload[key] = dict()
                        temp_payload[key]["description"] = val["description"]
                        if dict(val)["type"] == "array":
                            temp_payload[key]["type"] = "list"
                            temp_payload[key]["elements"] = "dict"
                        elif dict(val)["type"] == "dict":
                            temp_payload[key]["type"] = "dict"
                        temp_payload[key]["suboptions"] = dict()
                        for inside_key, inside_val in iteritems(
                            val["suboptions"]
                        ):
                            print(inside_key, inside_val)
                            temp_payload[key]["suboptions"][
                                inside_key
                            ] = dict()
                            if inside_val.get("description"):
                                temp_payload[key]["suboptions"][
                                    inside_key
                                ].update(
                                    {"description": inside_val["description"]}
                                )
                            else:
                                temp_payload[key]["suboptions"][
                                    inside_key
                                ].update({"description": "N/A"})
                            if inside_val["type"] == "dict":
                                temp_payload[key]["suboptions"][inside_key][
                                    "type"
                                ] = "dict"
                                temp_payload[key]["suboptions"][inside_key][
                                    "suboptions"
                                ] = {}
                                for inside_val_k, inside_val_v in iteritems(
                                    inside_val["suboptions"]
                                ):
                                    if inside_val_v.get("enum"):
                                        inside_val_v["choices"] = inside_val_v[
                                            "enum"
                                        ]
                                        del inside_val_v["enum"]
                                    temp_payload[key]["suboptions"][
                                        inside_key
                                    ]["suboptions"].update(
                                        {inside_val_k: inside_val_v}
                                    )
                            if (
                                inside_val["type"] == "string"
                                or inside_val["type"] == "str"
                            ):
                                temp_payload[key]["suboptions"][
                                    inside_key
                                ].update({"type": "str"})
                            if inside_val["type"] == "integer":
                                temp_payload[key]["suboptions"][
                                    inside_key
                                ].update({"type": "int"})
                            if (
                                inside_val["type"] == "boolean"
                                or inside_val["type"] == "bool"
                            ):
                                temp_payload[key]["suboptions"][
                                    inside_key
                                ].update({"type": "bool"})
                            if inside_val.get("enum"):
                                temp_payload[key]["suboptions"][
                                    inside_key
                                ].update({"choices": inside_val["enum"]})

    temp_json_payload = {}
    doc_option_generator(json_payload, temp_json_payload)
    module_description = ""
    if json_payload.get("description"):
        module_description = json_payload["description"]
    if json_payload.get("properties"):
        json_payload = temp_json_payload

    module_resource = " ".join(module_resource.split("_")).upper()
    module_obj = {
        "module": "{0}".format(module_name),
        "short_description": "Manages {0} resource module".format(
            module_resource
        ),
        "description": "{0}".format(module_description),
        "version_added": "{0}".format(module_version),
        "options": {
            "config": {
                "description": "A dictionary of {0} options".format(
                    module_resource
                ),
                "type": "list",
                "elements": "dict",
                "suboptions": json_payload,
            },
            "state": {
                "description": [
                    "The state the configuration should be left in",
                    "The state I(gathered) will get the module API configuration from the device and transform it into structured data in the format as per the module argspec and the value is returned in the I(gathered) key within the result.",
                ],
                "type": "str",
                "choices": ["merged", "replaced", "gathered", "deleted"],
            },
        },
        "author": "{0}".format(author),
    }

    json_obj = json.dumps(module_obj)
    with open(temp_data_file, "w+") as ff:
        yaml_obj = yaml.safe_load(json_obj)
        ydump = yaml.dump(yaml_obj)
        ff.write("""{0}""".format(ydump))


def convert_word_to_snake_case(word, global_var_mgmt_dict):
    upperc_only_word = None
    first_word = ""
    list_desc = re.compile("([A-Z]+[a-z]+|[A-Z][a-z]+|[A-Z]+)").findall(word)
    if list_desc:
        uppecase_word_len = word.split(re.compile("([A-Z]+)").findall(word)[0])
        if uppecase_word_len[0] != "":
            first_word_compile = re.compile("([a-z]+)").findall(word)
            if first_word_compile:
                first_word = first_word_compile[0] + "_"
            else:
                upperc_only_word = (
                    re.compile("([A-Z]+)").findall(word)[0].lower()
                )
    else:
        first_word = word
    if upperc_only_word:
        test = upperc_only_word
    else:
        list_desc = map(lambda x: x.lower(), list_desc)
        test = first_word + "_".join(list_desc)
    if word != test and test not in global_var_mgmt_dict:
        global_var_mgmt_dict.update({test: word})
    return test


def gen_dict_extract(key, var):
    if isinstance(var, dict):
        for k, v in iteritems(var):
            if k == key:
                yield v
                break
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            if isinstance(v, list):
                for each in v:
                    for result in gen_dict_extract(key, each):
                        yield result
                        break


def get_api_param_properties(object, api_object, data):
    def get_api_object(schema_path, data):
        for each in schema_path:
            if each == "#":
                post_object = data
            else:
                post_object = OrderedDict(post_object[each])
        return post_object

    if "properties" in api_object:
        return api_object
    post_schema_path = list(gen_dict_extract(object, api_object))[0].split("/")

    post_object = get_api_object(post_schema_path, data)

    for k, v in iteritems(post_object.get("properties")):
        if "$ref" in v:
            inbound_1st_level_schema_path = v["$ref"].split("/")
            temp_k_properties = get_api_object(
                inbound_1st_level_schema_path, data
            )
            if temp_k_properties.get("properties"):
                del post_object["properties"][k]["$ref"]
                post_object["properties"][k]["type"] = "array"
                post_object["properties"][k]["items"] = {
                    inbound_1st_level_schema_path[-1]: temp_k_properties[
                        "properties"
                    ]
                }
            else:
                post_object["properties"][k] = temp_k_properties
            if post_object["properties"][k].get("items") and isinstance(
                post_object["properties"][k]["items"], dict
            ):
                temp_param_key = {}
                for key, val in iteritems(
                    post_object["properties"][k]["items"]
                ):
                    if isinstance(val, dict):
                        for each_key, each_val in iteritems(val):
                            if "$ref" in each_val:
                                inbound_2nd_level_schema_path = each_val[
                                    "$ref"
                                ].split("/")
                                temp_k_properties = get_api_object(
                                    inbound_2nd_level_schema_path, data
                                )
                                if temp_k_properties.get("properties"):
                                    if (
                                        temp_k_properties.get("type")
                                        == "object"
                                    ):
                                        temp_k_properties["type"] = "array"
                                if key not in temp_param_key:
                                    temp_param_key.update(
                                        {
                                            key: {
                                                each_key: dict(
                                                    temp_k_properties[
                                                        "properties"
                                                    ]
                                                )
                                            }
                                        }
                                    )
                                else:
                                    temp_param_key[key].update(
                                        {
                                            each_key: dict(
                                                temp_k_properties["properties"]
                                            )
                                        }
                                    )
                            else:
                                if key not in temp_param_key:
                                    temp_param_key[key].update(
                                        {each_key: each_val}
                                    )
                                else:
                                    temp_param_key[key].update(
                                        {each_key: each_val}
                                    )
                post_object["properties"][k] = temp_param_key

        elif "items" in v and "$ref" in v["items"]:
            inbound_schema_path = v["items"]["$ref"].split("/")
            ref_object = get_api_object(inbound_schema_path, data)
            post_object["properties"][k]["items"] = {
                inbound_schema_path[-1]: ref_object
            }

    return get_api_param_properties("$ref", post_object, data)


def update_param_to_ansible_std(val, count=0):
    count += 1
    if val.get("type") == "string":
        val["type"] = "str"
    if val.get("type") == "integer":
        val["type"] = "int"
    if val.get("type") == "boolean":
        val["type"] = "bool"
    if val.get("type") == "array":
        val["type"] = "list"
        if "type" in val.get("items"):
            if val["items"]["type"] == "string":
                val["elements"] = "str"
            elif val["items"]["type"] == "integer":
                val["elements"] = "int"
            del val["items"]
    if val.get("format"):
        del val["format"]
    if val.get("enum"):
        val["choices"] = val["enum"]
        del val["enum"]
    if val.get("title"):
        val["description"] = val["title"]
        del val["title"]

    return val, count


def get_api_param_properties_recursively(
    object, api_object, data, global_var_mgmt_dict
):
    def get_api_object(schema_path, data):
        for each in schema_path:
            if each == "#":
                post_object = data
            else:
                post_object = OrderedDict(post_object[each])
        return post_object

    def recursive_stack_parse_ref(
        key, value, data, stack, parent_key_elements
    ):
        if "$ref" in value or ("items" in value and "$ref" in value["items"]):
            if "$ref" in value:
                stack.append("ref")
                path_url_split = dict(value)["$ref"].split("/")
            elif "items" in value and "$ref" in value["items"]:
                path_url_split = dict(v)["items"]["$ref"].split("/")
            post_object = get_api_object(path_url_split, data)
            stack.append(path_url_split[-1])
            if post_object.get("properties"):
                # child_stack = deque()
                temp_post_object = {}
                temp = {}
                for each_k, each_v in iteritems(post_object["properties"]):
                    if (
                        each_v.get("type") == "array" and each_v.get("items")
                    ) or "type" not in each_v:
                        temp.update({each_k: each_v})
                    else:
                        temp_post_object.update({each_k: each_v})
                if temp:
                    temp_post_object.update(temp)
                for each_k, each_v in iteritems(temp_post_object):
                    if each_v.get("$ref"):
                        stack.append("ref")
                    if "type" not in each_v:
                        stack.append(each_k)
                        recursive_stack_parse_ref(
                            each_k, each_v, data, stack, parent_key_elements
                        )
                    elif each_v.get("type") == "array" and each_v.get("items"):
                        stack.append(each_k)
                        recursive_stack_parse_ref(
                            each_k,
                            each_v["items"],
                            data,
                            stack,
                            parent_key_elements,
                        )
                    elif each_k in parent_key_elements:
                        stack.append(each_k)
                        stack.append(each_v)
                    else:
                        stack.append({each_k: each_v})
            else:
                stack.append(post_object)

    if "properties" in api_object:
        return api_object

    temp_val = list(gen_dict_extract(object, api_object))

    if "/" in temp_val[0]:
        post_schema_path = temp_val[0].split("/")
    else:
        post_schema_path = temp_val[0]
    if isinstance(post_schema_path, list):
        post_object = get_api_object(post_schema_path, data)
    elif isinstance(post_schema_path, dict) and post_schema_path.get(
        "properties"
    ):
        post_object = post_schema_path
    post_object_temp = None
    ref = False
    temp_post_object = {}
    if post_object.get("properties"):
        temp_post_object["properties"] = {}
        for k, v in iteritems(post_object["properties"]):
            if "-" in k:
                temp_k = "_".join(k.split("-"))
                global_var_mgmt_dict.update({temp_k: k})
            else:
                temp_k = convert_word_to_snake_case(k, global_var_mgmt_dict)
            temp_post_object["properties"][temp_k] = post_object["properties"][
                k
            ]
            parent_key_elements = []
            final_dict = {}
            stack = deque()
            path_url_split = None
            if "$ref" in v:
                ref = True
                path_url_split = dict(v)["$ref"].split("/")
            if "items" in v and "$ref" in v["items"]:
                ref = True
                path_url_split = dict(v)["items"]["$ref"].split("/")
            if "items" in v and "properties" in v["items"]:
                global_var_mgmt_dict_inside = dict()
                global_var_mgmt_dict_inside[temp_k] = dict()
                temp_post_object["properties"][temp_k]["suboptions"] = {}
                for inside_k, inside_v in iteritems(v["items"]["properties"]):
                    if "-" in inside_k:
                        inside_temp_k = "_".join(inside_k.split("-"))
                        global_var_mgmt_dict_inside[temp_k].update(
                            {inside_temp_k: inside_k}
                        )
                    else:
                        inside_temp_k = convert_word_to_snake_case(
                            inside_k, global_var_mgmt_dict
                        )
                        global_var_mgmt_dict_inside[temp_k].update(
                            {inside_temp_k: inside_k}
                        )
                    temp_post_object["properties"][temp_k]["suboptions"][
                        inside_temp_k
                    ] = post_object["properties"][k]["items"]["properties"][
                        inside_k
                    ]
                if temp_post_object["properties"][temp_k].get("items"):
                    del temp_post_object["properties"][temp_k]["items"]
            if path_url_split:
                post_object_temp = get_api_object(path_url_split, data)
                if (
                    not parent_key_elements
                    and post_object_temp
                    and post_object_temp.get("properties")
                ):
                    parent_key_elements = list(post_object_temp["properties"])
                if "name" in parent_key_elements:
                    parent_key_elements[
                        parent_key_elements.index("name")
                    ] = "name_parent"

            recursive_stack_parse_ref(k, v, data, stack, parent_key_elements)
            temp_key = None
            if stack:
                temp = {}
                temp_parent = []
                for each in parent_key_elements:
                    temp_parent.append(
                        convert_word_to_snake_case(each, global_var_mgmt_dict)
                    )
                parent_key_elements = temp_parent
                check_dict = False
                count = 0
                previous = False
                for i in range(len(stack)):
                    val = stack.pop()
                    if i == len(stack) and val == "ref":
                        continue
                    if val == "ref":
                        previous = True
                        continue
                    if val == "processPolicy":
                        pass
                    if val == "split" and i == 0:
                        continue
                    if (
                        not isinstance(val, dict)
                        and val not in parent_key_elements
                    ):
                        val = convert_word_to_snake_case(
                            val, global_var_mgmt_dict
                        )
                    if val in parent_key_elements:
                        if check_dict:
                            if temp.get("type"):
                                final_dict.update({val: temp})
                            else:
                                final_dict.update(
                                    {val: {"type": "dict", "suboptions": temp}}
                                )
                        temp = {}
                        continue
                    elif isinstance(val, dict) and previous:
                        final_dict.update(temp)
                        previous = False
                        temp = {}
                    if isinstance(val, dict):
                        check_dict = True
                        val, count = update_param_to_ansible_std(val, count)
                        temp.update(val)
                    else:
                        count += 1
                        temp = {val: temp}
                    if previous:
                        temp_key = list(temp.keys())[0]
                        if temp_key != "type":
                            if temp[temp_key].get(
                                "type"
                            ) == "array" or not temp[temp_key].get("type"):
                                temp[temp_key] = {
                                    "type": "dict",
                                    "suboptions": temp[temp_key],
                                }
                        previous = False
                if temp and not final_dict:
                    final_dict = temp

            if final_dict:
                final_dict = OrderedDict(reversed(list(iteritems(final_dict))))
                temp_post_object["properties"][temp_k] = {
                    "type": "list",
                    "elements": "dict",
                    "suboptions": {temp_key: final_dict},
                }
            elif ref and post_object_temp and path_url_split:
                temp_post_object["properties"][temp_k]["items"] = {
                    path_url_split[-1]: post_object_temp
                }
    post_object["properties"] = temp_post_object["properties"]
    return post_object


def ckp_params_fields_parsing(object_data, api_params, global_var_mgmt_dict):
    stack = deque()
    api_params_dict = OrderedDict()
    temp = OrderedDict()
    parent_key_elements = []
    for each in api_params:
        temp_k = each["name"]
        if "-" in temp_k:
            temp_k = "_".join(temp_k.split("-"))
            global_var_mgmt_dict.update({temp_k: each["name"]})
        stack.append(temp_k)
        parent_key_elements.append(temp_k)
        temp[temp_k] = OrderedDict({"description": each["description"]})
        for each_type in each["types"]:
            temp_type = {}
            for each_k, each_v in iteritems(each_type):
                if each_k == "object-name" and each_v != "java.lang.Object":
                    stack.append("object-name")
                    if temp_k not in global_var_mgmt_dict:
                        global_var_mgmt_dict.update({temp_k: each["name"]})

                    def get_child_params_recursively(
                        child_object_data,
                        request_field_name,
                        stack,
                        global_var_mgmt_dict,
                    ):
                        temp_child_type = {}
                        for each_obj in child_object_data:
                            if each_obj["name"] == request_field_name:
                                request_fields = each_obj["fields"]
                                for each_request_fields in request_fields:
                                    child_temp_k = each_request_fields["name"]
                                    if "-" in child_temp_k:
                                        child_temp_k = "_".join(
                                            child_temp_k.split("-")
                                        )
                                        global_var_mgmt_dict.update(
                                            {
                                                child_temp_k: each_request_fields[
                                                    "name"
                                                ]
                                            }
                                        )
                                    if child_temp_k not in stack:
                                        stack.append(child_temp_k)
                                    stack.append(
                                        {
                                            "description": each_request_fields[
                                                "description"
                                            ]
                                        }
                                    )
                                    for each_child_type in each_request_fields[
                                        "types"
                                    ]:
                                        temp_child_type = {}
                                        for (
                                            each_child_k,
                                            each_child_v,
                                        ) in iteritems(each_child_type):
                                            if each_child_k == "object-name":
                                                stack.append("object-name")
                                                get_child_params_recursively(
                                                    child_object_data,
                                                    each_child_v,
                                                    stack,
                                                    global_var_mgmt_dict,
                                                )
                                            elif (
                                                each_child_k == "valid-values"
                                            ):
                                                temp_child_type.update(
                                                    {"enum": each_child_v}
                                                )
                                            elif each_child_v == "list":
                                                temp_child_type[
                                                    "type"
                                                ] = "array"
                                            elif (
                                                each_child_v
                                                == "java.lang.Object"
                                            ):
                                                temp_child_type[
                                                    "type"
                                                ] = "array"
                                            elif (
                                                each_child_k == "element-type"
                                            ):
                                                temp_child_type.update(
                                                    {
                                                        "element-type": each_child_v[
                                                            "name"
                                                        ]
                                                    }
                                                )
                                            elif each_child_v == "boolean":
                                                temp_child_type[
                                                    "type"
                                                ] = each_child_v
                                            elif each_child_v == "integer":
                                                temp_child_type[
                                                    "type"
                                                ] = each_child_v
                                            else:
                                                temp_child_type[
                                                    "type"
                                                ] = each_child_v
                                    if temp_child_type:
                                        stack.append(temp_child_type)
                                break

                    get_child_params_recursively(
                        object_data, each_v, stack, global_var_mgmt_dict
                    )
                elif each_k == "valid-values":
                    temp_type.update({"enum": each_v})
                elif each_k == "element-type":
                    temp_type.update({"element-type": each_v["name"]})
                elif each_v == "object":
                    temp_type["type"] = "dict"
                elif each_v == "list":
                    temp_type["type"] = "array"
                    temp_type.update({"element-type": "string"})
                elif each_v == "java.lang.Object":
                    temp_type["type"] = "array"
                    temp_type.update({"element-type": "string"})
                elif each_v == "boolean":
                    temp_type["type"] = each_v
                elif each_v == "integer":
                    temp_type["type"] = each_v
                else:
                    temp_type["type"] = each_v
        temp_stack_val = {}
        if len(stack) > 1:
            temp_parent = stack.popleft()
            if "list" in stack:
                temp_stack_val[temp_parent] = {
                    "type": "list",
                    "elements": "dict",
                    "suboptions": OrderedDict(),
                }
            else:
                temp_stack_val[temp_parent] = {
                    "type": "dict",
                    "suboptions": OrderedDict(),
                }
            count = 0
            stack_len = len(stack)
            verify_temp_val = False
            try:
                for i in range(stack_len):
                    stack_val = stack.popleft()
                    if stack_val == "object-name" and i != 0:
                        child_param = {
                            "type": "dict",
                            "suboptions": OrderedDict(),
                        }
                        for j in range(i + 1, stack_len):
                            temp_val = stack.popleft()
                            if verify_temp_val == temp_val or (
                                isinstance(temp_val, dict)
                                and temp_val.get("type") == "object"
                            ):
                                verify_temp_val = True
                                break
                            if temp_val != "object-name" and not isinstance(
                                temp_val, dict
                            ):
                                child_param["suboptions"].update(
                                    {temp_val: {}}
                                )
                                child_temp_param = temp_val
                            elif isinstance(temp_val, dict):
                                child_param["suboptions"][
                                    child_temp_param
                                ].update(temp_val)
                                verify_temp_val = temp_val
                    if verify_temp_val:
                        temp_stack_val[temp_parent]["suboptions"].update(
                            {child_stack_param: child_param}
                        )
                        verify_temp_val = False
                        continue
                    if stack_val != "object-name" and not isinstance(
                        stack_val, dict
                    ):
                        temp_stack_val[temp_parent]["suboptions"].update(
                            {stack_val: {}}
                        )
                        child_stack_param = stack_val
                    elif isinstance(stack_val, dict):
                        temp_stack_val[temp_parent]["suboptions"][
                            child_stack_param
                        ].update(stack_val)
            except IndexError:
                pass
            stack = deque()
        else:
            stack.pop()
        if temp_stack_val:
            temp[temp_k].update(temp_stack_val[temp_k])
        elif temp_type:
            temp[temp_k].update(temp_type)
        api_params_dict.update(temp)
        temp = OrderedDict()
    return api_params_dict


def main():
    ####################################################
    #     str(sys.argv[0]) -> doc_generator.py
    #     str(sys.argv[1]) -> rm_swagger_json
    #     str(sys.argv[2]) -> api_object_path
    #     str(sys.argv[3]) -> module_name
    #     str(sys.argv[4]) -> module_version
    #     str(sys.argv[5]) -> resource
    #     str(sys.argv[6]) -> collection_org
    #     str(sys.argv[7]) -> collection_name
    #     str(sys.argv[8]) -> unique_key
    #     str(sys.argv[9]) -> author
    #     str(sys.argv[10])-> Temp Dir path
    ####################################################

    with open(str(sys.argv[1]), encoding="cp1252") as file:
        json_content = file.read()
        data = json.loads(json_content, object_pairs_hook=OrderedDict)
        request_fields = None
        if str(sys.argv[6]) == "checkpoint":
            if data.get("commands") and data.get("objects"):
                for each in data["commands"]:
                    if each["name"].get("web") == str(sys.argv[2]):
                        request = each["request"]
                        break
                for each in data["objects"]:
                    if each["name"] == request:
                        if (
                            each.get("fields")
                            and each.get("under-more-fields")
                            and each.get("required-fields")
                        ):
                            request_fields = (
                                each["required-fields"]
                                + each["fields"]
                                + each["under-more-fields"]
                            )
                        elif each.get("fields"):
                            request_fields = each["fields"]
                        break
        elif str(sys.argv[6]) in ["trendmicro", "fortinet"]:
            # TrendMicro
            # api_object = data["paths"]["/intrusionpreventionrules"]["post"]
            # Fortinet
            # api_object = data["paths"]["/firewall/policy"]["post"]
            api_object = data["paths"][str(sys.argv[2])]["post"]
        global_var_mgmt_dict = {}
        if request_fields:
            post_properties = OrderedDict()
            post_properties.update(
                {
                    "properties": ckp_params_fields_parsing(
                        data["objects"], request_fields, global_var_mgmt_dict
                    )
                }
            )
        else:
            # post_properties = get_api_param_properties_recursively(
            #     "$ref", api_object, data, global_var_mgmt_dict
            # )
            post_properties = get_api_param_properties_recursively(
                "schema", api_object, data, global_var_mgmt_dict
            )

        attribute_map_by_param = {}
        module_name = str(sys.argv[3])
        module_resource = str(sys.argv[5])
        module_version = str(sys.argv[4])
        author = str(sys.argv[9])

        temp_param_file = str(sys.argv[10]) + "/params.json"
        temp_data_file = str(sys.argv[10]) + "/data.yml"
        with open(temp_param_file, "w+") as ff:
            ff.write("""{0}""".format(json.dumps(global_var_mgmt_dict)))

        generate_documentation(
            post_properties,
            module_name,
            module_version,
            module_resource,
            author,
            temp_data_file,
        )


if __name__ == "__main__":
    main()
