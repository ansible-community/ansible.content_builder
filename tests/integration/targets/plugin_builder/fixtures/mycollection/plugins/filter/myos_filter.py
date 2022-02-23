#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The myos_filter filter plugin
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
name: myos_filter
author: Ansible Team
version_added: "1.0.0"
short_description: A demo filter plugin.
description: A demo filter plugin.
options:
  keyA:
    type: int
    description: Description for keyA.
    required: True
  keyB:
    type: str
    description: Description for keyB.
"""

EXAMPLES = """

"""

from ansible.errors import AnsibleFilterError
from ansible_collections.myorg.myos.plugins.plugin_utils.myos_filter import (
    myos_filter,
)
from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)

def _myos_filter(*args, **kwargs):
    keys = ['keyA', 'keyB']
    data = dict(zip(keys, args))
    data.update(kwargs)
    aav = AnsibleArgSpecValidator(
        data=data, schema=DOCUMENTATION, name="myos_filter"
    )
    valid, errors, updated_data = aav.validate()
    if not valid:
        raise AnsibleFilterError(errors)
    return myos_filter(**updated_data)

class FilterModule(object):
    """ myos_filter filter plugin"""

    def filters(self):
        """a mapping of filter names to functions"""
        return {"myos_filter": _myos_filter}
