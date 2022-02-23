# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the myos facts module.
"""


class FactsArgs(object):  # pylint: disable=R0903
    """ The arg spec for the myos facts module
    """

    def __init__(self, **kwargs):
        pass

    choices = [
        'all',
        'interfaces',
    ]

    argument_spec = {
        'gather_subset': dict(default=['!config'], type='list'),
        'gather_network_resources': dict(choices=choices,
                                         type='list'),
    }
