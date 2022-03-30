# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Test plugin file for myos_test
"""

from __future__ import absolute_import, division, print_function
from ansible_collections.ansible.utils.plugins.plugin_utils.base.utils import (
    _validate_args,
)
from ansible_collections.myorg.myos.plugin_utils.myos_test import (
    myos_test,
)

__metaclass__ = type

DOCUMENTATION = """
name: myos_test
author: Ansible Team
version_added: "1.0.0"
short_description: A demo test plugin.
description: A demo test plugin.
options:
  keyA:
    type: int
    description: Description for keyA.
    required: True
  keyB:
    type: str
    description: Description for keyB.
"""

EXAMPLES = r"""

"""

RETURN = """
# TO-DO: Enter return values here
"""


def _myos_test(keyA, keyB):
    """Implementation for myos_test"""
    # TO-DO: Remove quotes from the dict values for `params`
    params = {'keyA': 'keyA', 'keyB': 'keyB'}
    _validate_args("myos_test", DOCUMENTATION, params)

    # implement test logic here


class TestModule(object):
    """ myos_test test"""

    test_map = {"myos_test": _myos_test}

    def tests(self):
        return self.test_map
