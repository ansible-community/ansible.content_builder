# Copyright (c) 2020-2022 Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import ast


def get_doc(module):
    for node in ast.walk(ast.parse(module)):
        if isinstance(node, ast.Assign):
            if node.targets[0].id == "DOCUMENTATION":
                return node.value.s.strip()


class FilterModule(object):
    def filters(self):
        return {"get_doc": get_doc}
