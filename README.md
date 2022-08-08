# Ansible Plugin Builder Collection

This repository contains the `ansible.plugin_builder` Ansible Collection.

## Tested with Ansible

Tested with ansible-core 2.11 releases and the current development version of ansible-core.

## Installation

```
    pip install ansible-core
    ansible-galaxy collection install git+https://github.com/ansible-community/ansible.plugin_builder.git
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: ansible.plugin_builder
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Using this collection

build.yaml
```yaml
---
- hosts: localhost
  gather_facts: yes
  roles:
    - ansible.plugin_builder.run
```
MANIFEST.yaml
```yaml
---
collection:
  path: /path/to/collection
  namespace: test_namespace
  name: test_name
plugins:
  - type: action
    name: custom_action
    docstring: /path/to/docstring.yaml
  
  - type: cache
    name: custom_cache
    docstring: /path/to/docstring.yaml
  
  - type: filter
    name: custom_filter
    docstring: /path/to/docstring.yaml

  - type: test
    name: custom_test
    docstring: /path/to/docstring.yaml
  
  - type: lookup
    name: custom_lookup
    docstring: /path/to/docstring.yaml
```

```
ansible-playbook build.yaml -e manifest_file=MANIFEST.yaml 
```

## Supported plugins

| **Plugin Type**        | **Description**                                             |
|------------------------|-------------------------------------------------------------|
| action                 | Scaffold a action plugin                                    |
| cache                  | Scaffold a cache plugin                                     |
| filter                 | Scaffold a filter plugin                                    |
| test                   | Scaffold a test plugin                                      |
| lookup                 | Scaffold a lookup plugin                                    |
| module_network_cli     | Scaffold a Network Resource Module that support network_cli |
| module_network_netconf | Scaffold a Network Resource Module that supports netconf    |

## Options


## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
