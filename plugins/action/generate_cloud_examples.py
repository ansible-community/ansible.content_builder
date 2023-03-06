#!/usr/bin/env python3

import argparse
import collections
import io
from pathlib import Path
from typing import Dict, List, Any, Union
import re
import ruamel.yaml
import yaml
from ansible.plugins.action import ActionBase


class MissingDependency(Exception):
    # Raises exception when there is a missing dependency in the
    # integration tests picked up for EXAMPLES in the doc.
    pass


class ContentInjectionFailure(Exception):
    # Raises exception when the closing of the EXAMPLES block
    # is not updated or found.
    pass


TaskType = Dict[str, Any]


def _task_to_string(task: TaskType) -> str:
    sanatized_task = {
        k: v for k, v in task.items() if k not in ["ignore_errors", "tags"]
    }
    a = io.StringIO()
    _yaml = ruamel.yaml.YAML()
    _yaml.width = 160  # type: ignore
    _yaml.dump([sanatized_task], a)
    a.seek(0)
    return a.read().rstrip()


def get_nested_tasks(task: TaskType, target_dir: Path) -> List[TaskType]:
    tasks: List[TaskType] = []
    if "include_tasks" in task:
        tasks += get_tasks(target_dir, play=task["include_tasks"])
    elif "import_tasks" in task:
        tasks += get_tasks(target_dir, play=task["import_tasks"])
    else:
        tasks.append(task)

    return tasks


def get_tasks(target_dir: Path, play: str = "main.yml") -> List[TaskType]:
    tasks: List[TaskType] = []
    current_file = target_dir / play
    data = yaml.load(current_file.read_text(), Loader=yaml.FullLoader)

    for task in data:
        if "include_tasks" in task:
            tasks += get_tasks(target_dir, play=task["include_tasks"])
        elif "import_tasks" in task:
            tasks += get_tasks(target_dir, play=task["import_tasks"])
        elif "block" in task:
            for item in task["block"]:
                tasks += get_nested_tasks(item, target_dir)
        elif "always" in task:
            for item in task["always"]:
                tasks += get_nested_tasks(item, target_dir)
        else:
            tasks.append(task)

    return tasks


def naive_variable_from_jinja2(raw: str) -> Union[None, str]:
    jinja2_string = raw.strip(" ")

    if "lookup(" in jinja2_string:
        return None
    if m := re.search(r".*?{{\s*(.*?(?!}}).*?)\s*}}", jinja2_string):
        jinja2_string = m.group(1)
    if m := re.search(r"^\((.*)\).*", jinja2_string):
        jinja2_string = m.group(1)
    if jinja2_string.startswith("not "):
        jinja2_string = jinja2_string[4:]
    variable = jinja2_string.split(".")[0]
    if re.search("[/:]", variable):
        return None
    if variable == "item":
        return None
    if " " in variable:
        return None
    return variable


def list_dependencies(value: Any) -> List[str]:
    dependencies = []
    if isinstance(value, str):
        if value[0] != "{":
            return []
        variable = naive_variable_from_jinja2(value)
        if variable:
            return [variable]
    for k, v in value.items():
        if isinstance(v, dict):
            dependencies += list_dependencies(v)
        elif isinstance(v, list):
            for i in v:
                dependencies += list_dependencies(i)
        elif not isinstance(v, str):
            pass
        elif "{{" in v:
            variable = naive_variable_from_jinja2(v)
            if variable:
                dependencies.append(variable)
        elif k == "with_items":
            dependencies.append(v.split(".")[0])
    dependencies = [i for i in dependencies if not i.startswith("_")]
    return sorted(list(set(dependencies)))


# Use tags tagged with tags: docs in the integration tests to extract to use as EXAMPLES
def extract(
    tasks: List[TaskType],
    collection_name: str,
    dont_look_up_vars: List[str],
    task_selector: str = "name",
) -> Dict[str, Any]:
    by_modules: Dict[str, Any] = collections.defaultdict(dict)
    registers: Dict[str, Any] = {}

    def valid_task(task: Dict[str, Any]) -> bool:
        if task_selector == "tag":
            return "docs" in task.get("tags", [])
        elif task_selector == "name":
            try:
                return not task["name"].startswith("_")
            except KeyError:
                return False
        else:
            raise ValueError

    for task in tasks:
        depends_on = []
        for r in list_dependencies(value=task):
            if r in dont_look_up_vars:
                continue
            if r not in registers:
                raise MissingDependency(
                    f"task: {task['name']}\nCannot find key '{r}' in the known variables: {registers.keys()}"
                )
                continue
            depends_on += registers[r]

        if "register" in task:
            if not valid_task(task):
                print(f"Hiding register {task['register']}.")
                del task["register"]
            else:
                registers[task["register"]] = depends_on + [task]

        if "ansible.builtin.set_fact" in task:
            for fact_name in task["ansible.builtin.set_fact"]:
                registers[fact_name] = depends_on + [task]

        if "set_fact" in task:
            for fact_name in task["set_fact"]:
                registers[fact_name] = depends_on + [task]

        module_fqcn = None
        for key in list(task.keys()):
            if key.startswith(collection_name):
                module_fqcn = key
                break
        if not module_fqcn:
            continue

        if module_fqcn not in by_modules:
            by_modules[module_fqcn] = {
                "blocks": [],
            }
        if valid_task(task):
            by_modules[module_fqcn]["blocks"] += depends_on + [task]

    return by_modules


def flatten_module_examples(tasks: List[TaskType]) -> str:
    result: str = ""
    seen: List[TaskType] = []

    for task in tasks:
        if task in seen:
            continue
        seen.append(task)
        result += "\n" + _task_to_string(task) + "\n"
    return result


def inject(
    target_dir: Path, extracted_examples: Dict[str, Dict[str, List[Dict[str, Any]]]]
) -> None:
    module_dir = target_dir / "plugins" / "modules"
    for module_fqcn in extracted_examples:
        module_name = module_fqcn.split(".")[-1]
        module_path = module_dir / (module_name + ".py")
        if module_path.is_symlink():
            continue

        examples_section_to_inject = flatten_module_examples(
            extracted_examples[module_fqcn]["blocks"]
        )
        new_content = ""
        in_examples_block = False
        closing_pattern = None
        for l in module_path.read_text().split("\n"):
            if m := re.search(r"^EXAMPLES\s+=\s+(|r)('{3}|\"{3})$", l):
                closing_pattern = m.group(2)
                in_examples_block = True
                new_content += l + "\n" + examples_section_to_inject.lstrip("\n")
            elif closing_pattern and l == closing_pattern:
                in_examples_block = False
                new_content += l + "\n"
            elif in_examples_block:
                continue
            else:
                new_content += l + "\n"
        if in_examples_block:
            raise ContentInjectionFailure(
                "The closing of the EXAMPLES block was not found."
            )
        if closing_pattern is None:
            raise ContentInjectionFailure("The EXAMPLES block was not updated.")
        new_content = new_content.rstrip("\n") + "\n"
        print(f"Updating {module_name}")
        module_path.write_text(new_content)


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
    
        galaxy_file = args.get("target_dir") + "/galaxy.yml"
        galaxy = yaml.safe_load(Path(galaxy_file).open())
        vars_file = task_vars['vars']['role_path'] + "/vars/main.yaml"
        vars = yaml.safe_load(Path(vars_file).open())
        collection_name = f"{galaxy['namespace']}.{galaxy['name']}"
        tasks = []
        test_scenarios_dirs = [
            Path(args.get("target_dir")) / Path(i)
            for i in vars["examples"][collection_name]["load_from"]
        ]
        for scenario_dir in test_scenarios_dirs:
            if not scenario_dir.is_dir():
                continue
            if scenario_dir.name.startswith("setup_"):
                continue
            task_dir = scenario_dir / "tasks"
            tasks += get_tasks(task_dir)
    
        extracted_examples = extract(
            tasks,
            collection_name,
            dont_look_up_vars=vars["examples"][collection_name]["dont_look_up_vars"],
            task_selector=vars["examples"][collection_name]["task_selector"],
        )
        inject(Path(args.get("target_dir")), extracted_examples)
        return self._result
