# Ansible Content Builder Collection

This repository contains the `ansible.content_builder` Ansible Collection.

## Tested with Ansible

Tested with ansible-core 2.13 releases and the current development version of ansible-core.

## Installation

```
pip install ansible-core
ansible-galaxy collection install git+https://github.com/ansible-community/ansible.content_builder.git
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: ansible.content_builder
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Using this collection

build.yaml
```yaml
---
- hosts: localhost
  gather_facts: yes
  roles:
    - ansible.content_builder.run
```
MANIFEST.yaml
### For Network collection scaffolding
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

### Ressource module scaffolding generated using OpenApi based JSON 

Giving `module_generator` as an input to Ansible.plugin builder scaffolding tool helps Ansible content developers scaffold and output Ansible Resource Modules (RM) based out of OPENAPI based swagger JSON file, using HTTPAPI connection plugin for the platform configuration.

**Capabilities:**
- Use a pre-defined OPENAPI based swagger JSON file or other JSON file to scaffold a resource module in an Ansible Collection.
- Generates working resource module file `<vendor>_<resource>.py` and relevant action logic file both `action/<vendor>_<resource>.py`.

**Input Parameters:**

- *rm_swagger_json*: Swagger JSON/JSON file where OEMs API with all of its REST operations are defined.
- *rm_dest*: Destination folder where the user wants the output of the scaffolding tool to be stored.
- *api_object_path*: API for which resource module needs to be generated by the tool.
- *module_name*: Ansible module name against the API.
- *resource*: API resource.
- *collection_org*: Ansible collection org name.
- *collection_name*: Ansible collection name.
- *unique_key*: Unique key for API.

#### Builing a new module/collection:

Currently, the tool is optimised to parse Trendmicro Deepsecurity, Fortinet and CheckPoint swagger JSON files to output Resource modules for respective platforms.

#### Examples:

#### 1. Trendmicro Deepsecurity

MANIFEST.yaml:
```yaml
---
module_generator:
  rm_swagger_json: /swagger_tm.json
  rm_dest: /tmp/trendmicro/deepsec
  api_object_path: /intrusionpreventionrules
  module_name: 'deepsec_intrusion_prevention_rules'
  module_version: 1.2.0
  resource: intrusion_prevention_rules
  collection_org: trendmicro
  collection_name: deepsec
  unique_key: ""
  author: "Ansible Security Automation Team (@justjais) <https://github.com/ansible-security>"
```

#### 2. Fortinet

MANIFEST.yaml:
```yaml
---
module_generator:
  rm_swagger_json: /FortiOS_7.0.3_Configuration_API_firewall.json
  rm_dest: /tmp/fortinet/fortios
  api_object_path: /firewall/policy
  module_name: fortios_firewall_policy
  module_version: 1.2.0
  resource: firewall_policy
  collection_org: fortinet
  collection_name: fortios
  unique_key: policyid
  author: "Ansible Security Automation Team (@justjais) <https://github.com/ansible-security>"
```

#### 3. CheckPoint

MANIFEST.yaml:
```yaml
---
module_generator:
  rm_swagger_json: ~/Sumit/ansible_fork/collections/security_collections/doc_generator/apis_ckp.json
  rm_dest: /tmp/checkpoint/mgmt
  api_object_path: add-access-rule
  module_name: 'cp_mgmt_access_rules_global'
  module_version: 1.2.0
  resource: access_rules
  collection_org: checkpoint
  collection_name: mgmt
  unique_key: ""
  author: "Ansible Security Automation Team (@justjais) <https://github.com/ansible-security>"
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
| module                 | Scaffold a Resource Module generated using OpenApi JSON file|

## Options


## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
