#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus lldp_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.lldp_interfaces.lldp_interfaces import Lldp_interfacesArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    int_range_to_list
)


class Lldp_interfacesFacts(object):
    """ The awplus lldp_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Lldp_interfacesArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    @staticmethod
    def get_device_data(connection):
        return connection.get('show running-config interface')

    @staticmethod
    def get_int_brief(connection):
        int_brief = connection.get("show interface brief").splitlines()
        return [i.split()[0].strip() for i in int_brief][1:]

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for lldp_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_device_data(connection)
        int_list = self.get_int_brief(connection)

        resources = data.split("!")

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_configs(self.generated_spec, resource, int_list)
                if obj:
                    objs.extend(obj)

        ansible_facts['ansible_network_resources'].pop('lldp_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['lldp_interfaces'] = [utils.remove_empties(cfg) for cfg in params['config']]

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_configs(self, spec, conf, int_list):
        """
        Render config as a list of dictionaries

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: list
        :returns: List of generated config
        """
        configs = []
        name = utils.parse_conf_arg(conf, 'interface')
        if name:
            if not name.startswith('port'):
                return None

            names = int_range_to_list(name, int_list)
            for name in names:
                configs.append(self.parse_run_int(spec, conf, name))

        return configs

    def parse_run_int(self, spec, conf, name):
        """
        Create a dictionary structure of the interface config

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :param name: Name of the interface
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)
        config['name'] = name

        tlvs = re.findall(r'.*lldp tlv-select (\S+)', conf, re.M)
        if tlvs:
            if tlvs[0] == 'all':
                tlvs = list(config['tlv_select'].keys())
            for tlv in tlvs:
                config['tlv_select'][tlv.replace('-', '_')] = True

        transmit = re.search(r'lldp.*transmit', conf, re.M)
        if transmit:
            config['transmit'] = False

        receive = re.search(r'lldp.*receive', conf, re.M)
        if receive:
            config['receive'] = False

        no_med_tlv = utils.parse_conf_arg(conf, 'no lldp med-tlv-select')
        if no_med_tlv:
            non_med_tlvs = re.findall(r'(\S+)', no_med_tlv)
            if non_med_tlvs[0] == 'all':
                non_med_tlvs = list(config['med_tlv_select'].keys())
            for non_med in non_med_tlvs:
                config['med_tlv_select'][non_med.replace('-', '_')] = False
        med_tlv = utils.parse_conf_arg(conf, '^\\slldp med-tlv-select')
        if med_tlv:
            config['med_tlv_select']['inventory_management'] = True

        return utils.remove_empties(config)
