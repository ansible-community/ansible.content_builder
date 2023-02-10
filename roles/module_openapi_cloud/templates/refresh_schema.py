import argparse
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect the schema definition.")
    parser.add_argument(
        "--schema-dir",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="location where to store the collected schemas (default: .)",
    )
    
    parser.add_argument(
        "--modules",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="location where to store the collected schemas (default: .)",
    )
    
    args = parser.parse_args()
    
    RESOURCES = []
    resource_file = args.modules / "modules.yaml"
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
        import q
        q(schema)
        file_name = re.sub("::", "_", type_name)
        if not args.schema_dir.exists():
            pathlib.Path(args.schema_dir).mkdir(parents=True, exist_ok=True)
        schema_file = args.schema_dir / f"{file_name}.json"
        schema_file.write_text(json.dumps(schema, indent=2))


if __name__ == "__main__":
    main()
