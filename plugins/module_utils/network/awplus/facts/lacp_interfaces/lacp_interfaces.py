#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus lacp_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.lacp_interfaces.lacp_interfaces import Lacp_interfacesArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    int_range_to_list
)


class Lacp_interfacesFacts(object):
    """ The awplus lacp_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Lacp_interfacesArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_run_conf(self, connection):
        return connection.get('show running-config interface')

    def get_int_brief(self, connection):
        int_brief = connection.get('show interface brief').splitlines()
        return [i.split()[0].strip() for i in int_brief][1:]

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for lacp_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            # typically data is populated from the current device configuration
            data = self.get_run_conf(connection)
        int_list = self.get_int_brief(connection)

        resources = data.split('!')

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(resource, int_list)
                if obj:
                    objs.extend(obj)

        ansible_facts['ansible_network_resources'].pop('lacp_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['lacp_interfaces'] = [utils.remove_empties(cfg) for cfg in params['config']]

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, conf, int_list):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        match = re.search(r'interface (\S+)', conf)
        intfs = match.group(1) if match else ''

        if not intfs.startswith('port'):
            return []

        interfaces = int_range_to_list(intfs, int_list) if '-' in intfs else [intfs]

        conf_list = []
        for interface in interfaces:
            conf_list.append(self.parse_config(conf, interface))

        return conf_list

    def parse_config(self, conf, intf):
        """
        Translate a given config into dictionary and delete keys from spec for null values

        :param conf: The configuration
        :param intf: name of the interface
        :rtype: dict
        :returns: The generated config
        """
        config = deepcopy(self.generated_spec)
        config['name'] = intf

        port_priority = utils.parse_conf_arg(conf, 'lacp port-priority')
        if port_priority:
            config['port_priority'] = port_priority

        timeout = utils.parse_conf_arg(conf, 'lacp timeout')
        if timeout:
            config['timeout'] = timeout

        return utils.remove_empties(config)
