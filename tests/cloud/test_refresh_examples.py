#!/usr/bin/env python3

import ansible_collections.ansible.content_builder.plugins.action.generate_cloud_examples as ge

import pytest
import pathlib


def test__task_to_string():
    my_task = {
        "name": "Some example",
        "commad": "My fancy command",
        "vars": {"foo": "bar"},
    }
    expectation = (
        "- name: Some example\n"
        "  commad: My fancy command\n"
        "  vars:\n"
        "    foo: bar"
    )
    assert ge._task_to_string(my_task) == expectation


def test_get_nested_tasks(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "my_playbook.yml"

    p.write_text("- command: ls from include_task\n")
    my_task = {"include_tasks": "my_playbook.yml"}
    assert ge.get_nested_tasks(my_task, d) == [
        {"command": "ls from include_task"}
    ]

    p.write_text("- command: ls from import_task\n")
    my_task = {"import_tasks": "my_playbook.yml"}
    assert ge.get_nested_tasks(my_task, d) == [
        {"command": "ls from import_task"}
    ]

    my_task = {"command": "ls from task"}
    assert ge.get_nested_tasks(my_task, d) == [
        {"command": "ls from task"}
    ]


naive_variables = [
    ("{{ foo_bar }}", "foo_bar"),
    ("{{ not foo_bar }}", "foo_bar"),
    ("{{ foo_bar.key }}", "foo_bar"),
    ("{{ aws_region }}{{ item.zone }}", "aws_region"),
    ("foobar{{ bar.key }}", "bar"),
    ("{{ item }}", None),
    ("{{ lookup('lookup are not supported') }}", None),
    ("https://foo.bar", None),
    (
        '{{ (lib_items.value|selectattr("name", "equalto", "golden_image")|first).id }}',
        "lib_items",
    ),
    # This is too complicated. Let's just ignore it.
    (
        "{{ {} | combine({ my_new_disk.id: {'policy': my_storage_policy.policy, 'type': 'USE_SPECIFIED_POLICY'} }) }}",
        None,
    ),
]


@pytest.mark.parametrize("in_val,out_val", naive_variables)
def test_naive_variable_from_jinja2(in_val, out_val):
    assert ge.naive_variable_from_jinja2(in_val) == out_val


def test_list_dependencies():
    assert ge.list_dependencies({"var": "{{ bar }}"}) == ["bar"]
    assert ge.list_dependencies(
        {"var": {"a": 1, "b": ["a", "b"]}, "with_items": "castor.lapon"}
    ) == ["castor"]


my_tasks = [
    {
        "name": "This would be a great example",
        "foo.bar.my_module": {"first_param": 1, "second_param": "a_string"},
    },
    {
        "foo.bar.my_module": {"first_param": 1, "second_param": "a_string"},
        "tags": ["docs"],
    },
    {
        "name": "_name starts with an underscope",
        "foo.bar.my_module": {"first_param": 1, "second_param": "a_string"},
    },
    {"foo.bar.my_module": {"first_param": 1, "second_param": "a_string"}},
    {"foo.bar.another_module": {}, "ingore_errors": True},
    {"another.collection.another_module": {"g:": 1}},
    {"assert": {"that": ["something"]}, "ignore_errors": True},
]


def test_extract_identify_valid_block_using_name():
    expectation = {
        "foo.bar.another_module": {"blocks": []},
        "foo.bar.my_module": {
            "blocks": [
                {
                    "name": "This would be a great example",
                    "foo.bar.my_module": {"first_param": 1, "second_param": "a_string"},
                }
            ]
        },
    }
    assert (
        ge.extract(my_tasks, "foo.bar", []) == expectation == expectation
    )


def test_extract_identify_valid_block_using_tag():
    expectation = {
        "foo.bar.another_module": {"blocks": []},
        "foo.bar.my_module": {
            "blocks": [
                {
                    "foo.bar.my_module": {"first_param": 1, "second_param": "a_string"},
                    "tags": ["docs"],
                }
            ]
        },
    }
    assert (
        ge.extract(my_tasks, "foo.bar", [], task_selector="tag")
        == expectation
    )


def test_extract_with_dependencies():
    my_tasks = [
        {
            "name": "This would be a great example",
            "another.collect.prepare_stuff": {
                "first_param": 1,
                "second_param": "a_string",
            },
            "register": "my_stuff",
        },
        {"name": "Define some facts", "set_fact": {"a_fact": True}},
        {
            "name": "This would be a great example",
            "foo.bar.my_module": {
                "first_param": "{{ a_fact }}",
                "second_param": "{{ my_stuff }}",
            },
        },
    ]
    expectation = {
        "foo.bar.my_module": {
            "blocks": [
                {"name": "Define some facts", "set_fact": {"a_fact": True}},
                {
                    "name": "This would be a great example",
                    "another.collect.prepare_stuff": {
                        "first_param": 1,
                        "second_param": "a_string",
                    },
                    "register": "my_stuff",
                },
                {
                    "name": "This would be a great example",
                    "foo.bar.my_module": {
                        "first_param": "{{ a_fact }}",
                        "second_param": "{{ my_stuff }}",
                    },
                },
            ]
        }
    }

    assert ge.extract(my_tasks, "foo.bar", []) == expectation


def test_extract_missing_dependency():
    my_tasks = [
        {
            "name": "This would be a great example",
            "foo.bar.my_module": {
                "first_param": "{{ a_fact }}",
                "second_param": "{{ my_stuff }}",
            },
        },
    ]
    with pytest.raises(ge.MissingDependency):
        ge.extract(my_tasks, "foo.bar", [])


def test_extract_with_dont_look_up_vars():
    my_tasks = [
        {
            "name": "This would be a great example",
            "foo.bar.my_module": {
                "first_param": "{{ a_fact }}",
                "second_param": "{{ my_stuff }}",
            },
        },
    ]
    ge.extract(my_tasks, "foo.bar", ["a_fact", "my_stuff"])


def test_flatten_module_examples():
    my_input = [
        {"name": "First module", "foo.bar.my_module": {}},
        {"name": "Second module", "foo.bar.my_module": {"param": 1}},
    ]
    expectation = (
        "\n"
        "- name: First module\n"
        "  foo.bar.my_module: {}\n"
        "\n"
        "- name: Second module\n"
        "  foo.bar.my_module:\n"
        "    param: 1\n"
    )
    assert ge.flatten_module_examples(my_input) == expectation


def test_flatten_module_examples_with_dup():
    task = {"name": "Dup module", "foo.bar.my_module": {}}
    my_input = [task] * 5
    print(ge.flatten_module_examples(my_input))
    expectation = "\n" "- name: Dup module\n" "  foo.bar.my_module: {}\n"
    assert ge.flatten_module_examples(my_input) == expectation


def test_inject_content(tmp_path):
    target_dir = tmp_path / "my_collection"
    module_dir = target_dir / "plugins" / "modules"
    module_dir.mkdir(parents=True)
    my_module = module_dir / "my_module.py"
    my_module.write_text(
        "blabal\n"
        "EXAMPLES = r'''\n"
        "existing example\n'''\n"
        "the end of the module\n"
    )
    extracted_example = {
        "foo.bar.my_module": {
            "blocks": [
                {
                    "name": "A good fit fo the EXAMPLEs block",
                    "foo.bar.my_module": {"param": 1},
                }
            ]
        }
    }
    ge.inject(target_dir, extracted_example)
    assert my_module.read_text() == (
        "blabal\n"
        "EXAMPLES = r'''\n"
        "- name: A good fit fo the EXAMPLEs block\n"
        "  foo.bar.my_module:\n"
        "    param: 1\n"
        "'''\n"
        "the end of the module\n"
    )

    my_module.write_text("blabal\n" "EXAMPLES = r'''\n" "existing example\n")
    with pytest.raises(ge.ContentInjectionFailure):
        ge.inject(target_dir, extracted_example)
