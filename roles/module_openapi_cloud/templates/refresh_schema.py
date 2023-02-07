import pathlib
import re
from typing import Dict, List, Optional, TypedDict
import boto3
from generator import CloudFormationWrapper
import json
import yaml
from gouttelette.utils import camel_to_snake


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

    for key, value in schema.items():
        if key != "anyOf":
            if isinstance(value, list):
                elems = []
                for v in value:
                    if isinstance(v, list):
                        elems.extend(
                            [camel_to_snake(p.split("/")[-1].strip()) for p in v]
                        )
                    else:
                        elems.append(camel_to_snake(v.split("/")[-1].strip()))

                schema[key] = elems

    return schema


def refresh_schema(schema_dir, modules):
    RESOURCES = []
    resource_file = modules / "modules.yaml"
    res = resource_file.read_text()
    for i in yaml.safe_load(res):
        RESOURCES = i.get("RESOURCES", "")
        if RESOURCES:
            break

    for type_name in RESOURCES:
        print("Collecting Schema")
        print(type_name)
        cloudformation = CloudFormationWrapper(boto3.client("cloudformation"))
        raw_content = cloudformation.generate_docs(type_name)
        schema = generate_schema(raw_content)
        file_name = re.sub("::", "_", type_name)
        if not schema_dir.exists():
            pathlib.Path(schema_dir).mkdir(parents=True, exist_ok=True)
        schema_file = schema_dir / f"{file_name}.json"
        schema_file.write_text(json.dumps(schema, indent=2))
