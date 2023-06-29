#!/usr/bin/env python3


from dataclasses import dataclass
from typing import Any, Dict, List
import jinja2
import baron
import redbaron
import yaml
import re
import copy
import subprocess
from pathlib import Path
from functools import lru_cache


def jinja2_renderer(
    template_file: str, role_path: Path, collection: str, **kwargs: Dict[str, Any]
) -> str:
    templateLoader = jinja2.FileSystemLoader(
        role_path + "/templates/module_directory/" + collection
    )
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file)
    return template.render(kwargs)


def format_documentation(documentation: Any) -> str:
    yaml.Dumper.ignore_aliases = lambda *args: True  # type: ignore

    def _sanitize(input: Any) -> Any:
        if isinstance(input, str):
            return input.replace("':'", ":")
        if isinstance(input, list):
            return [l.replace("':'", ":") for l in input]
        if isinstance(input, dict):
            return {k: _sanitize(v) for k, v in input.items()}
        if isinstance(input, bool):
            return input
        raise TypeError

    keys = [
        "module",
        "short_description",
        "description",
        "options",
        "author",
        "version_added",
        "requirements",
        "extends_documentation_fragment",
        "seealso",
        "notes",
    ]
    final = "r'''\n"
    for i in keys:
        if i not in documentation:
            continue
        if isinstance(documentation[i], str):
            sanitized = _sanitize(documentation[i])
        else:
            sanitized = documentation[i]
        final += yaml.dump({i: sanitized}, indent=4, default_flow_style=False)
    final += "'''"
    return final


def indent(text_block: str, indent: int = 0) -> str:
    result: str = ""

    for line in text_block.split("\n"):
        result += " " * indent
        result += line
        result += "\n"
    return result


def get_module_from_config(module: str, target_dir: Path) -> Dict[str, Any]:
    module_file = Path(target_dir) / "modules.yaml"
    raw_content = module_file.read_text()

    for i in yaml.safe_load(raw_content):
        if module in i:
            return i[module] or {}
    raise KeyError


def python_type(value: str) -> str:
    TYPE_MAPPING = {
        "array": "list",
        "boolean": "bool",
        "integer": "int",
        "number": "int",
        "object": "dict",
        "string": "str",
    }
    if isinstance(value, list):
        return TYPE_MAPPING.get(value[0], value)
    return TYPE_MAPPING.get(value, value)


def run_git(git_dir: str, *args: List[Any]) -> List[Any]:
    cmd = [
        "git",
        "--git-dir",
        git_dir,
    ]
    for arg in args:
        cmd.append(arg)
    r = subprocess.run(cmd, text=True, capture_output=True)
    return r.stdout.rstrip().split("\n")


@lru_cache(maxsize=None)
def file_by_tag(git_dir: str) -> Dict[str, Any]:
    tags = run_git(git_dir, "tag")

    files_by_tag: Dict[str, Any] = {}
    for tag in tags:
        files_by_tag[tag] = run_git(git_dir, "ls-tree", "-r", "--name-only", tag)

    return files_by_tag


def get_module_added_ins(module_name: str, git_dir: str) -> Dict[str, Any]:
    added_ins: Dict[str, Any] = {"module": None, "options": {}}
    module = f"plugins/modules/{module_name}.py"

    for tag, files in file_by_tag(git_dir).items():
        if "rc" in tag:
            continue
        if module in files:
            if not added_ins["module"]:
                added_ins["module"] = tag
            content = "\n".join(
                run_git(
                    git_dir,
                    "cat-file",
                    "--textconv",
                    f"{tag}:{module}",
                )
            )
            try:
                ast_file = redbaron.RedBaron(content)
            except baron.BaronError as e:
                print(f"Failed to parse {tag}:plugins/modules/{module_name}.py. {e}")
                continue
            doc_block = ast_file.find(
                "assignment", target=lambda x: x.dumps() == "DOCUMENTATION"
            )
            if not doc_block or not doc_block.value:
                print(f"Cannot find DOCUMENTATION block for module {module_name}")
            doc_content = yaml.safe_load(doc_block.value.to_python())
            for option in doc_content["options"]:
                if option not in added_ins["options"]:
                    added_ins["options"][option] = tag

    return added_ins


def scrub_keys(
    a_dict: Dict[str, Any], list_of_keys_to_remove: List[str]
) -> Dict[str, Any]:
    """Filter a_dict by removing unwanted keys: values listed in list_of_keys_to_remove"""
    if not isinstance(a_dict, dict):
        return a_dict
    return {
        k: v
        for k, v in (
            (k, scrub_keys(v, list_of_keys_to_remove)) for k, v in a_dict.items()
        )
        if k not in list_of_keys_to_remove
    }


def ignore_description(a_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter a_dict by removing description fields.
    Handle when 'description' is a module suboption.
    """
    a_dict_copy = copy.copy(a_dict)
    if not isinstance(a_dict, dict):
        return a_dict

    for k, v in a_dict_copy.items():
        if k == "description":
            if isinstance(v, dict):
                ignore_description(v)
            else:
                a_dict.pop(k)
        ignore_description(v)


def ensure_description(
    element: Dict[str, Any], *keys: List[Any], default: str = "Not Provived."
) -> Dict[str, Any]:
    """
    Check if *keys (nested) exists in `element` (dict) and ensure it has the default value.
    """
    if isinstance(element, dict):
        for key, value in element.items():
            if key == "suboptions":
                ensure_description(value, *keys)

            if isinstance(value, dict):
                for akey in keys:
                    if akey not in value:
                        element[key][akey] = [default]
                for k, v in value.items():
                    ensure_description(v, *keys)

    return element


def _camel_to_snake(name: str, reversible: bool = False) -> str:
    def prepend_underscore_and_lower(m: str) -> str:
        return "_" + m.group(0).lower()

    if reversible:
        upper_pattern = r"[A-Z]"
    else:
        # Cope with pluralized abbreviations such as TargetGroupARNs
        # that would otherwise be rendered target_group_ar_ns
        upper_pattern = r"[A-Z]{3,}s$"

    s1 = re.sub(upper_pattern, prepend_underscore_and_lower, name)
    # Handle when there was nothing before the plural_pattern
    if s1.startswith("_") and not name.startswith("_"):
        s1 = s1[1:]
    if reversible:
        return s1

    # Remainder of solution seems to be https://stackoverflow.com/a/1176023
    first_cap_pattern = r"(.)([A-Z][a-z]+)"
    all_cap_pattern = r"([a-z0-9])([A-Z]+)"
    s2 = re.sub(first_cap_pattern, r"\1_\2", s1)
    return re.sub(all_cap_pattern, r"\1_\2", s2).lower()


def camel_to_snake(data: Any, alias=True) -> Any:
    """
    It performs a transformation from CamelCase to snake_case and set an aliases list
    with the original CamelCase as item if alias=True.
    When alias=False, it perfoms only the transformation from CamelCase to snake_case.
    """
    if isinstance(data, str):
        return _camel_to_snake(data)
    elif isinstance(data, list):
        return [_camel_to_snake(r) for r in data]
    elif isinstance(data, dict):
        b_dict: Dict[str, Any] = {}
        for k in data.keys():
            snaked_case_key = _camel_to_snake(k)
            if isinstance(data[k], dict):
                b_dict[snaked_case_key] = camel_to_snake(data[k])
                # Add aliases for each parameter exclusing these module specific ones
                if alias and k not in (
                    "description",
                    "type",
                    "enum",
                    "choices",
                    "suboptions",
                    "elements",
                    "default",
                    "options",
                ):
                    b_dict[snaked_case_key].update({"aliases": [k]})
            else:
                b_dict[snaked_case_key] = data[k]
        return b_dict


@dataclass
class UtilsBase:
    name: str

    def is_trusted(self, target_dir: Path) -> bool:
        try:
            get_module_from_config(self.name, target_dir)
            return True
        except KeyError:
            print(f"- do not build: {self.name}")
            return False

    def write_module(self, target_dir: Path, content: str) -> None:
        module_dir = Path(target_dir + "/plugins/modules")
        module_dir.mkdir(parents=True, exist_ok=True)
        module_py_file = module_dir / "{name}.py".format(name=self.name)
        module_py_file.write_text(content)
