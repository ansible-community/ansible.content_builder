# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""
The myos_lookup lookup plugin
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
name: myos_lookup
author: Ansible Team
version_added: "1.0.0"
short_description: A demo lookup plugin.
description: A demo lookup plugin.
options:
  keyA:
    type: int
    description: Description for keyA.
    required: True
"""

RETURN = """
# TO-DO: Enter return values here
"""

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible_collections.myorg.myos.plugin_utils.myos_lookup import (
    myos_lookup,
)
from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        if isinstance(terms, list):
            keys = ['keyA']
            terms = dict(zip(keys, terms))
        terms.update(kwargs)
        aav = AnsibleArgSpecValidator(
            data=terms, schema=DOCUMENTATION, name="myos_lookup"
        )
        valid, errors, updated_data = aav.validate()
        if not valid:
            raise AnsibleLookupError(errors)
        res = myos_lookup(**updated_data)
        return res
