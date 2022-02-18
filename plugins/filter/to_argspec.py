# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    convert_doc_to_ansible_module_kwargs,
)


def to_argspec(documentation):
    return convert_doc_to_ansible_module_kwargs(documentation)


class FilterModule(object):
    def filters(self):
        return {"to_argspec": to_argspec}
