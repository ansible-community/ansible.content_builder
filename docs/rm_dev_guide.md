# THE RESOURCE MODULE DOC

### Is your model ready?

```
git clone https://github.com/ansible-network/resource_module_models.git
```

Once the above repo is cloned, go to the desired collection and add your model there. Reach out to the Ansible Network team to get it _approved_. You'll find us at `#ansible-network` on [irc.libera.chat](https://libera.chat/) or at `ansiblenetwork.slack.com`.

##### Helpful Links-

- [Ansible 101: Part 1: In the beginning there was YAML](https://www.redhat.com/en/blog/ansible-101-part-1-beginning-there-was-yaml)
- [YAML syntax](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html)
- [Learn X in Y minutes](https://learnxinyminutes.com/docs/yaml/)

### Let’s get started with the Resource Module development.

At first, we would need a builder for our whole code base to get scaffolded from a tool - `content_builder`

```
pip install black==22.3.0 jsonschema jinja2==3.0.3 ansible-core
ansible-galaxy collection install git+https://github.com/ansible-community/ansible.content_builder.git
```

The collection _dir_ have the following structure, follow the Github _namespaces_ for the setup under ansible collection

```
~/../../collections
❯ tree -L 3
├── collections
│   └── ansible_collections
│       ├── ansible
│       │   ├── netcommon
│       │   └── utils
│       ├── ansible_network
│       ├── cisco
│       │   └── ios
│       ├── junipernetworks
│       │   └── junos
│       └── vyos
│           └── vyos

```

Once the content_builder is installed and the target collection repo is cloned in the desired location we can work on the development of our module.
Using the tool to generate the base-level code with which we proceed.

```
❯ cat content_builder_run.yml
---
- name: Scaffold boiler plate code for resource modules
  hosts: localhost
  gather_facts: true
  roles:
    - ansible.content_builder.run

```
```
❯ cat MANIFEST.yml
---
---
collection:
  path: /home/{user}/{S}/{A}/collections/ansible_collections/{network_os}/{network_os}
  namespace: {network_org}
  name: {network_os}
plugins:
  - type: module_network_cli
    name: {network_os}_{resource}
    docstring: /../resource_module_models/models/{network_os}/{{module}}/{network_os}_{resource}.yaml
    resource: {resource}
```

```
❯ ansible-playbook content_builder_run.yml -e manifest_file=MANIFEST.yaml
```

Post execution of the above command there should be few new files in your branch ready for the development of the resource module.

##### Important links at this point -

- Understanding RMs
  - [Ansible Network Resource Modules: Deep Dive on Return Values](https://www.ansible.com/blog/ansible-network-resource-modules-deep-dive-on-return-values)
  - [Developing network resource modules](https://docs.ansible.com/ansible/latest/network/dev_guide/developing_resource_modules_network.html)
  - [Getting started with Route Maps Resource Modules](https://www.ansible.com/blog/getting-started-with-route-maps-resource-modules)
- Debug Ansible resource module
  - [Debugging Ansible Network Modules with VSCode](https://github.com/KB-perByte/debuggingNetworkResourceModule/blob/master/README.md)
  - [Debugging Ansible Navigator with VSCode](https://github.com/shatakshiiii/debuggingNavigator/blob/main/README.md)
  - [Debugging modules](https://docs.ansible.com/ansible/latest/dev_guide/debugging.html)

# Introduction to RM files -

Looking at the collection where the new resource module is to be created after scaffolding the boiler plate code we should see the following new files already added -

`{network_os}_{resource}.py` - the entry point to the Resource Module code and the module documentation resides here. To change or update any argspec attribute during development we need to make the required change here directly in the docstring and then rerun the `rm_builder_run.yml` with _docstring_ var commented out.

```
../collections/ansible_collections/{network_os}/{network_os}/plugins/modules/{network_os}_{resource}.py
```

`{resource}.py` - under `facts` directory. The code in this file is responsible for converting native on-box configuration to Ansible structured data as per the argspec of the module by using the list of parsers defined in rm_templates/{resource}.py.The on-box config can either be fetched from the target device or from the value set in the `running_config` key in the task when the module is run with `state: parsed`. The call to get data from the target device is often wrapped within a method. This is done to facilitate easier mocking when writing unit tests.

```
../collections/ansible_collections/{network_os}/{network_os}/plugins/module_utils/network/{network_os}/facts/{resource}/{resource}.py
```

`facts.py` - You need to manually append the existence of your new resource module’s Facts class to the `FACTS_RESOURCE_SUBSET` dictionary in this file for facts to be generated as the call for facts is from a common instance i.e netcommon
The import -

```
from
ansible_collections.{network_os}.{network_os}.plugins.module_utils.network.{network_os}.facts.{resource}.{resource}
import (
  Logging_globalFacts,
)
```

The entry under global Var -

```
FACT_RESOURCE_SUBSETS = dict({resource}={resource}Facts,)
```

```
../collections/ansible_collections/{network_os}/{network_os}/plugins/module_utils/network/{network_os}/facts/facts.p
y
```

`logging_global.py` - The `argspec` file is the python level representation of your model. You may never need to edit it manually, change the model in the module file and content_builder should take care of updating it.

```
../collections/ansible_collections/{network_os}/{network_os}/plugins/module_utils/network/{network_os}/argspec/{resource}/{resource}.py
```

`logging_global.py` - the `rm_template` is one of the most vital components of a Resource Module since the conversion of native on-box configuration to structured data and vice-versa is facilitated by the parser templates that are defined in this file. Time to spin up regex/ jinja templating skills for this file. The better they are the easier it would be to get a higher score in the module's Unit Test Coverage (UTC).

```
../collections/ansible_collections/{network_os}/{network_os}/plugins/module_utils/network/{network_os}/rm_templates/{resource}.py
```

##### Helpful Links

- Regex parsers
  - [Pythex Regex parser](https://pythex.org/)
  - [Regex101](https://regex101.com/)
- Jinja2 parsers
  - [J2 Live Parser](http://jinja.quantprogramming.com/)
  - [Ansible Template Tester](https://ansible.sivel.net/test/)

`Logging_global.py` - the `config` file contains all the core logic of how the execution should behave in various states. In here you get _want_ [the playbook] and _have_ [the config that came from the facts rendered]
All the states and their comparison logic goes here.

```
/home/sagpaul/Work/bannerNconfig/collections/ansible_collections/{network_os}/{network_os}/plugins/module_utils/network/{network_os}/argspec/{resource}/{resource}.py
```

And, You might see a couple of *\_*init*\_*.py files generated,required for Ansible tests to pass!

## PHASE - 1 Gathering facts from the target device

The first step in building a resource module is to write facts code that converts device native configuration to structured data. This is done by comparing the device config with a set of pre-defined “Parser Templates” that define regexs to parse the native config.

Both the list of templates and the config are fed to an object of the NetworkTemplate class, on which the `parse()` method is then invoked. The output of the `parse()` method is semi-structured data that might need some additional updates to match the module’s argspec format. ref: [prefix_lists facts](https://github.com/ansible-collections/cisco.nxos/blob/2ea1935043bc5e607fb73a2192e20055b0be9e6a/plugins/module_utils/network/nxos/facts/prefix_lists/prefix_lists.py#L44)

Before finally rendering this data as facts, it is validated against the module’s argspec by the validate_config() method which fails if the data does not match the schema defined in the argspec.

## Anatomy of a Parser Template:

`name`
The name or unique identifier of the parser template.

`getval`
A regular expression using named capture groups to store the extracted data.Here
goes a regex that can break a command or a part of the command that is read from the device config and this contributes to generating facts from device native config. NOTE- This regex is not for validation, as this will not be used while forming the commands so we can just use simple regex forms to fragment the command and assign it to variables to use while we make our facts.

`setval`
This is used to generate device native config from Ansible structured data. It can either be a Python function or a Jinja2 template.

`result`-
A data tree, populated as a template, from the parsed data.This is where we generate the facts with the help of variables that are formed via the regex fragmentation we did in _getval_ It may match the part of facts the whole parser is written for i.e argspec i.e model.

`remval`-
(Optional) This is used to specify a command to negate an attribute. It can either be a Python function or a Jinja2 template. This is usually not needed, as in most cases simply negating the command generated by `setval` does the job.
However, this comes in handy when the command to remove an attribute is significantly different from `setval`.

`compval`-
(Optional) This is to be used for a complex model where parsers are broken down into multiple ones and are then referenced like namespaces. By default, the name of the parser itself is used to extract an attribute for want and have dictionaries.

For example:

```
want = {'k1': {'k2': {'k3': 'newval', ‘k4’: 'anotherval'}}}
have = {'k1': {'k2': {'k3': 'oldval', ‘k4’: 'anotherval'}}}
```

With parser name `'k1.k2.k3'`, the RMEngineBase will extract the value of the nested key `'k3'` from both _want_ and _have_ and then compare it in order to decide if an update is required. In this case, it will compare `'k3': 'newval'` and `'k3': 'oldval'`. However, if the parser template has `compval: k1.k2` defined, the value of the key `k2`(which is a dictionary itself) will be used. So here, the comparison will happen between `'k2': {'k3':'newval', k4: 'anotherval'}` and `{'k3': 'oldval', k4: 'anotherval'}`

`shared`-
(Optional) The shared key makes the parsed values available to the rest of the parser
entries until matched again. This enables the data/result of the parser to be shared among other parsers for reuse.

Example parsers -

```
switch(config)# ip prefix-list AllowPrefix description allows engineering server
```

Given the set of commands the parser _can_ look like -
ref : [prefix_list model](https://github.com/ansible-network/resource_module_models/blob/master/models/nxos/prefix_list/prefix_lists.yaml)

```
PARSERS =[{
            "name": "description",
            "getval": re.compile(
                r"""
                ^(?P<afi>ip|ipv6)
                \sprefix-list
                \s(?P<name>\S+)
                \sdescription\s(?P<description>.+)\s*
                $""", re.VERBOSE),
            "setval": "{{ 'ip' if afi == 'ipv4' else afi }} prefix-list {{ name }} description {{ description }}",
            "result": {
                "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}": {
                    "afi": "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}",
                    "prefix_lists": {
                        "{{ name }}": {
                            "name": "{{ name }}",
                            "description": "{{ description }}",
                        }
                    }
                },
            },
        },]
```

ref : [rm_template prefix_list](https://github.com/ansible-collections/cisco.nxos/blob/main/plugins/module_utils/network/nxos/rm_templates/prefix_lists.py)

Having setval ready at this point is not required, we can start off by executing our first playbook

```
---
- name: check GATHERED state
  hosts: your.host.name
  gather_facts: no
  tasks:
  - name: Gather logging config
    vyos.vyos.vyos_logging_global:
      state: gathered
```

```
---
- name: check PARSED state
  hosts: your.host.name
  gather_facts: no
  tasks:
  - name: Parse the provided configuration
    register: result
    vyos.vyos.vyos_logging_global:
      running_config: "{{ lookup('file', 'raw_vyos.cfg') }}"
      state: parsed
```

`raw_vyos.cfg`

This is just a flat file that holds the config that we get after the show commands are executed on the target device.

You should have a working facts code as of now! And the _gathered & parsed_ state should work before you proceed further.

##### Note

If there is a _list of items_ in the generated facts, it is suggested to sort them before they are rendered, in order to to get consistent output across different Python versions. This also helps with assertions while working on Unit or Integration Tests.

## PHASE - 2 THE CONFIG: MERGED and other STATEs

Let’s talk about the different [states](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html#network-resource-module-states)!

`MERGED` -

```
|     WANT     |    HAVE     |    Output    |  Comment  |
| :----------: | :---------: | :----------: | :-------: |
| {A, B, C, D} |   {A,B,E}   |    {C,D}     |  Changed  |
|      {}      | {A,B,C,D,E} |      {}      | No change |
| {A, B, C, D} |     {}      | {A, B, C, D} |  Changed  |
```

`REPLACED`- _rA - replace A_

```

|   WANT    |     HAVE     |       Output        |    Comment    |
| :-------: | :----------: | :-----------------: | :-----------: |
| {A, C, D} | {A, B, E, F} | {rA, B, E, F, C, D} | Changed A,C,D |

```

`OVERRIDDEN`- _nA - Negate A_

```

|     WANT     |    HAVE     |        Output         |  Comment  |
| :----------: | :---------: | :-------------------: | :-------: |
| {A, B, C, D} |   {A,B,E}   |   {A, B, nE, C, D}    |  Changed  |
| {A, B, C, D} |     {}      |     {A, B, C, D}      |  Changed  |
| {A, B, C, D} |   {E,F,G}   | {nE,nF,nG,A, B, C, D} |  Changed  |

```

`DELETED`-

```

|     WANT     |    HAVE     |      Output      |  Comment  |
| :----------: | :---------: | :--------------: | :-------: |
|      {}      | {A,B,C,D,E} | {nA,nB,nC,nD,nE} |  Changed  |
| {A, B, C, D} |     {}      |        {}        | No Change |
| {A, B, C, D} |   {E,F,G}   |        {}        | No Change |

```

`RENDERED`- Pass in a config with the rendered state it is supposed to tell you all the set of commands that would be formed on the supplied config (without actually connecting to the target device), it is different from check mode.

`PARSED`- The parsed state is just opposite to the rendered state it tells you how the invocation/facts would look like when you supply the `running_config` raw config from a device.

##### Some important links at this point-

- Parsing semi-structured text with Ansible
  - [Parsing the CLI](https://docs.ansible.com/ansible/latest/network/user_guide/cli_parsing.html)
- Working with command output and prompts in network modules
  - [Handling prompts](https://docs.ansible.com/ansible/latest/network/user_guide/network_working_with_command_output.html)
- Network Debug and Troubleshooting Guide
  - [Debugging network Modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_debug_troubleshooting.html)

## Config code -

The config side code is the place where all operational states are being handled, this file generates the final set of commands that would be pushed to the target device.

At first we have the class variable `self.parsers` that should contains the list of parsers that are defined for that module, later this variable is fed to the base class compare method to compare the want and have by resolving the namespace like representation of the parsers to compare on a granular level and generate the _setvals_ on behalf of the parsers for which the comparison is done.

The parsers may or may not reside under a single class variable, that depends on the complexity of module and decision of segregating the parser lists to support he main comparison code.

The `execute_module()` method handles the call to the `generate_commands()` method where the actual logical comparison takes place.

With the _want_ and _have,_ which represents the playbook and the facts are to be processed to be in a similar structure that can be compared. The implementation of `list_to_dict` on every attribute is imp on the entry point of config code before it starts getting processed on the basis of states. As the `compare()` method understands it better i.e a comparison of two dictionary of dictionaries is easier and more efficient than a comparison of two lists of dictionaries. Hence, to optimally leverage the RMEngineBase, it is important that we convert all lists to dicts to dicts of dicts before starting with the comparison process.

##### Example list to dict :

- [cisco.nxos.route_maps](https://github.com/ansible-collections/cisco.nxos/blob/main/plugins/module_utils/network/nxos/config/route_maps/route_maps.py#L190)
- [arista.eos.bpg_global](https://github.com/ansible-collections/arista.eos/blob/main/plugins/module_utils/network/eos/config/bgp_global/bgp_global.py#L365-L396)
- [cisco.iosxr.bgp_global](https://github.com/ansible-collections/cisco.iosxr/blob/main/plugins/module_utils/network/iosxr/config/bgp_global/bgp_global.py#L376-L407)

---

##### Note -

With the config development in place, there are few things to keep a note of to make the code clean and reusable by the rest of the modules within the same platform,

```

..collections/ansible_collections/{network_os}/{network_os}/plugins/module_
utils/network/{network_os}/utils/utils.py

```

At the above path, `utils.py` creates a set of defined methods that includes flattening the config or processing the list*to_dict operations for that platform.Adding a generic method here and making the whole module reuse that existing code adds up to the code quality.
...
Back to config, how the \_setvals* are picked up after the compare method is at a point to generate the commands that are finally used to apply the necessary comparison.

So, the compare method on comparison of two dicts refers to it by the name of the parsers and tries to match that with the defined list of parsers in the config code. Adding the parser names in namespace format helps the compare method to reduce the namespace based on the dictionary it is looking at and does the setval computation on the basis of that. There is no direct relation between the _result_ key and _setval_ key int he parsers. The data available at setvals to generate the command may or may not be aligned with the facts/results from parsers. It depends on the flattening logic written in config which molds our have and want data or better I say wantd and haved to be easily compared. Here if a dict contains

##### Example compare call :

- [cisco.nxos.route_maps](https://github.com/ansible-collections/cisco.nxos/blob/main/plugins/module_utils/network/nxos/config/route_maps/route_maps.py#L157)

```

haved = { 'key1' : { 'key2' : 100 , }}
wanted = { 'key1' : { 'key2' : 10 , }}

```

A parser named `key1` will do the compare and push the whole dict for being processed in _setvals_. Whereas a parser named `key1.key2` will do the comparison on a level under `key2` as per the above example.

Happy contribution!
