# Myorg Myos Collection

This repository contains the `myorg.myos` Ansible Collection.

## Tested with Ansible

Tested with the current Ansible 2.9, and ansible-core 2.11 releases and the current development version of ansible-core. Ansible versions before 2.9.10 are not supported.

## External requirements

Some modules and plugins require external libraries. Please check the requirements for each plugin or module you use in the documentation to find out which requirements are needed.

## Included content

Please check the included content on the [Ansible Galaxy page for this collection](https://galaxy.ansible.com/myorg/myos).

## Using this collection

```
    ansible-galaxy collection install myorg.myos
```
You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: myorg.myos
```

To upgrade the collection to the latest available version, run the following command:

```bash
ansible-galaxy collection install myorg.myos --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax where `X.Y.Z` can be any [available version](https://galaxy.ansible.com/myorg/myos):

```bash
ansible-galaxy collection install myorg.myos:==X.Y.Z
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
