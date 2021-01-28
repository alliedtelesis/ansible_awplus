#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus l2_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.l2_interfaces.l2_interfaces import L2_interfacesArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    int_range_to_list
)


class L2_interfacesFacts(object):
    """ The awplus l2_interfaces fact class
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

    def get_run_conf(self, connection):
        return connection.get("show running-config interface")

    def get_int_brief(self, connection):
        int_brief = connection.get("show interface brief").splitlines()
        return [i.split()[0].strip() for i in int_brief][1:]

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for l2_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_run_conf(connection)
        int_list = self.get_int_brief(connection)

        resources = data.split('!')

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(resource, int_list)
                if obj:
                    objs.extend(obj)

        ansible_facts['ansible_network_resources'].pop('l2_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['l2_interfaces'] = [utils.remove_empties(cfg) for cfg in params['config']]

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
        intfs = match.group(1)
        conf_list = []

        if not intfs.startswith('po') and not intfs.startswith('sa'):
            return []

        interfaces = int_range_to_list(intfs, int_list) if '-' in intfs else [intfs]

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
        config["name"] = intf

        mode = utils.parse_conf_arg(conf, "switchport mode")
        if mode == "access":
            has_access = utils.parse_conf_arg(conf, "switchport access vlan")
            if has_access:
                config["access"] = {"vlan": int(has_access)}

        trunk = dict()
        native_vlan = utils.parse_conf_arg(conf, "native vlan")
        if native_vlan and native_vlan != "none":
            trunk["native_vlan"] = int(native_vlan)
        allowed_vlan = utils.parse_conf_arg(conf, "allowed vlan add")
        if allowed_vlan:
            trunk["allowed_vlans"] = allowed_vlan.split(",")
        config["trunk"] = trunk
        return utils.remove_empties(config)
