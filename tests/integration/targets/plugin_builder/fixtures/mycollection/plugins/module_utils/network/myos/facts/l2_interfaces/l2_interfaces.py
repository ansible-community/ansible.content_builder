#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The myos l2_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils._text import to_bytes
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.myorg.myos.plugins.module_utils.network.myos.argspec.l2_interfaces.l2_interfaces import L2_interfacesArgs
from ansible.module_utils.six import string_types
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


class L2_interfacesFacts(object):
    """ The myos l2_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = L2_interfacesArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for l2_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not HAS_LXML:
            self._module.fail_json(msg='lxml is not installed.')

        if not data:
            config_filter = """
                <configuration>
                  <resource>
                  </resource>
                </configuration>
                """
            data = connection.get_configuration(filter=config_filter)

        if isinstance(data, string_types):
            data = etree.fromstring(to_bytes(data,
                                             errors='surrogate_then_replace'))

        resources = data.xpath('configuration/resources/resource')
        if connection:  # just for linting purposes, remove
            pass

        if not data:
            # typically data is populated from the current device configuration
            # data = connection.get('show running-config | section ^interface')
            # using mock data instead
            data = ("resource rsrc_a\n"
                    "  a_bool true\n"
                    "  a_string choice_a\n"
                    "  resource here\n"
                    "resource rscrc_b\n"
                    "  key is property01 value is value end\n"
                    "  an_int 10\n")

        # split the config into instances of the resource
        resource_delim = 'resource'
        find_pattern = r'(?:^|\n)%s.*?(?=(?:^|\n)%s|$)' % (resource_delim,
                                                           resource_delim)
        resources = [p.strip() for p in re.findall(find_pattern,
                                                   data,
                                                   re.DOTALL)]

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.append(obj)

        facts = {}
        if objs:
            facts['resource'] = []
            params = utils.validate_config(self.argument_spec,
                                           {'config': objs})
            for cfg in params['config']:
                facts['resource'].append(utils.remove_empties(cfg))


        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)

        config['name'] = utils.get_xml_conf_arg(conf, 'name')
        config['some_value'] = utils.get_xml_conf_arg(conf, 'some_value')

        return utils.remove_empties(config)
