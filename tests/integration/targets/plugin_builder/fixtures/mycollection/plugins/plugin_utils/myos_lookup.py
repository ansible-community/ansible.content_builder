#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The myos_lookup filter plugin
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleFilterError

def _raise_error(msg):
    """Raise an error message, prepend with filter name
    :param msg: The message
    :type msg: str
    :raises: AnsibleError
    """
    error = "Error when using plugin 'myos_lookup': {msg}".format(msg=msg)
    raise AnsibleFilterError(error)


def myos_lookup():
    """myos_lookup implementation
    """
    # Enter plugin logic here
    # This method will be invoked from the main plugin class
    pass