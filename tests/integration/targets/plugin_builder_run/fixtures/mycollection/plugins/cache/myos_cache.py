# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
name: myos_cache
author: Ansible Team
version_added: "1.0.0"
short_description: A demo cache plugin.
description: A demo cache plugin.
options:
  keyA:
    type: int
    description: Description for keyA.
    required: True
    ini:
      - key: myos_caching_keya
        section: defaults
  keyB:
    type: str
    description: Description for keyB.
    ini:
      - key: myos_caching_keyb
        section: defaults
'''

from ansible.plugins.cache import BaseCacheModule


class CacheModule(BaseCacheModule):
    """
    A myos_cache caching plugin.
    """

    def get(self, key):
        pass

    def set(self, key, value):
        pass

    def keys(self):
        pass

    def contains(self, key):
        pass

    def delete(self, key):
        pass

    def flush(self):
        pass
