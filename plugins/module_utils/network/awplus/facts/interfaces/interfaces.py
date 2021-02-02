#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.interfaces.interfaces import InterfacesArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    int_range_to_list
)


class InterfacesFacts(object):
    """ The awplus interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = InterfacesArgs.argument_spec
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
        return connection.get("show running-config interface")

    def get_int_brief(self, connection):
        int_brief = connection.get("show interface brief").splitlines()
        return [i.split()[0].strip() for i in int_brief][1:]

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for interfaces
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
                obj = self.render_config(self.generated_spec, resource, int_list)
                if obj:
                    objs.extend(obj)

        if int_list:  # add interfaces not shown in running-config
            for interface in int_list:
                obj = self.render_config(self.generated_spec, "interface " + interface, deepcopy(int_list))
                if obj:
                    objs.extend(obj)

        ansible_facts['ansible_network_resources'].pop('interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['interfaces'] = [utils.remove_empties(cfg) for cfg in params['config']]

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf, int_list):
        """ Render config for either a range or a single interface

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config as a list
        """
        intf_configs = []
        match = re.search(r"interface (\S+)", conf)
        if not match:
            return []

        interfaces = int_range_to_list(match.group(1), int_list)
        if not interfaces:
            return[]

        for interface in interfaces:
            if interface in int_list:
                intf_configs.append(self.parse_config(spec, conf, interface))
                int_list.remove(interface)
        return intf_configs

    def parse_config(self, spec, conf, intf):
        """ Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)
        config["name"] = intf
        config["description"] = utils.parse_conf_arg(conf, "description")
        if utils.parse_conf_arg(conf, "speed"):
            config["speed"] = int(utils.parse_conf_arg(conf, "speed"))
        if utils.parse_conf_arg(conf, "mtu"):
            config["mtu"] = int(utils.parse_conf_arg(conf, "mtu"))
        config["duplex"] = utils.parse_conf_arg(conf, "duplex")
        enabled = utils.parse_conf_cmd_arg(conf, "shutdown", False)
        config["enabled"] = enabled if enabled is not None else True
        return utils.remove_empties(config)
