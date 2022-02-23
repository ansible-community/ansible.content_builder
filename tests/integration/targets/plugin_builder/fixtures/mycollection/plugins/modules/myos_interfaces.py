#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for myos_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: myos_interfaces
version_added: 1.0.0
short_description: 'Manages interface attributes of MyOS Interfaces'
description: This module manages the interface attributes of MyOS interfaces.
authors: Ansible Network Team
notes:
  - Tested against MyOS 1.0.0
options:
  config:
    description: A dictionary of interface options
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Full name of interface, e.g. Ethernet1/1, port-channel10.
        type: str
        required: true
      description:
        description:
          - Interface description.
        type: str
      enabled:
        description:
          - Administrative state of the interface.
            Set the value to C(true) to administratively enable the interface
            or C(false) to disable it
        type: bool
        default: true
      speed:
        description:
          - Interface link speed. Applicable for Ethernet interfaces only.
        type: str
      mode:
        description:
          - Manage Layer2 or Layer3 state of the interface.
            Applicable for Ethernet and port channel interfaces only.
        choices: ['layer2','layer3']
        type: str
      mtu:
        description:
          - MTU for a specific interface. Must be an even number between 576 and 9216.
            Applicable for Ethernet interfaces only.
        type: str
      duplex:
        description:
          - Interface link status. Applicable for Ethernet interfaces only.
        type: str
        choices: ['full', 'half', 'auto']
  state:
    description:
      - The state the configuration should be left in.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - gathered
      - parsed
      - rendered
    default: merged
"""

EXAMPLES = """
# Using myos_interfaces

- myorg.myos.myos_interfaces:
    config:
      - name: Ethernet1/1
        description: Test
      - name: Ethernet1/2
        description: Test-2
"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.myorg.myos.plugins.module_utils.network.myos.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.myorg.myos.plugins.module_utils.network.myos.config.interfaces.interfaces import (
    Interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=InterfacesArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
