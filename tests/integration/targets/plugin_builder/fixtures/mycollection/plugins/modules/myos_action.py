#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
module: myos_action
author: Ansible Team
short_description: A demo action plugin
description: A demo action plugin
version_added: 1.0.0
options:
  keyA:
    type: str
    description: Description for keyA.
    required: True
  keyB:
    type: str
    description: Description for keyB.
"""

EXAMPLES = r"""
# Using myos_action

- myorg.myos.myos_action:
    keyA: test
    keyB: test_2
"""

RETURN = r"""
# TO-DO: Enter return values here
"""
