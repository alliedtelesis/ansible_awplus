#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus class_maps fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.class_maps.class_maps import Class_mapsArgs


class Class_mapsFacts(object):
    """ The awplus class_maps fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Class_mapsArgs.argument_spec
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
    def get_class_map_conf(connection):
        return connection.get("show class-map")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for class_maps
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if connection:  # just for linting purposes, remove
            pass

        if not data:

            data = self.get_class_map_conf(connection)
        resources = data.split('\n\n')

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('class_maps', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['class_maps'] = params['config']

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
        tcp_patterns = (r'(ack|fin|psh|rst|syn|urg)', r'Match TCP Flags')

        if re.search(r'CLASS-MAP-NAME', conf):
            for item in conf.split('\n'):
                name_match = re.search(r'CLASS-MAP-NAME: (\d+|\S+)', item)
                if name_match:
                    config["name"] = name_match.group(1)

                access_group_match = re.search(r'QOS-ACCESS-LIST-NAME: (\d+|\S+)', item)
                if access_group_match:
                    config["access_group"] = access_group_match.group(1)

                dscp_match = re.search(r'Match IP DSCP: (\d+)', item)
                if dscp_match:
                    config["dscp"] = dscp_match.group(1)

                ip_precedence_match = re.search(r'Match IP precedence: (\d+)', item)
                if ip_precedence_match:
                    config["ip_precedence"] = ip_precedence_match.group(1)

                cos_match = re.search(r'Match CoS: (\d+)', item)
                if cos_match:
                    config["cos"] = cos_match.group(1)

                tcp_flags_match = re.findall(tcp_patterns[0], item) if re.search(tcp_patterns[1], item) else None
                if tcp_flags_match:
                    flags = {}
                    for flag in tcp_flags_match:
                        flags[f'{flag}'] = True
                    false_flags = set(flags) ^ set(['urg', 'ack', 'rst', 'fin', 'psh', 'syn'])
                    for flag in false_flags:
                        flags[f'{flag}'] = False
                    config["tcp_flags"] = flags

                mac_type_match = re.search(r'Match Mac Type: (\d+) (\S+)', item)
                if mac_type_match:
                    config["mac_type"] = mac_type_match.group(2)

                eth_format_match = re.search(r'Match Eth Format: (\S+)', item)
                if eth_format_match:
                    config["eth_format"] = eth_format_match.group(1)

                eth_protocol_match = re.search(r'Match Protocol: (\S+)', item)
                if eth_protocol_match:
                    config["eth_protocol"] = eth_protocol_match.group(1)

                inner_cos_match = re.search(r'Match Inner CoS: (\d+)', item)
                if inner_cos_match:
                    config["inner_cos"] = inner_cos_match.group(1)

                inner_vlan_match = re.search(r'Match Inner VLAN: (\d+)', item)
                if inner_vlan_match:
                    config["inner_vlan"] = inner_vlan_match.group(1)

                vlan_match = re.search(r'Match vlan: (\d+)', item)
                if vlan_match:
                    config["vlan"] = vlan_match.group(1)

        config = utils.remove_empties(config)
        return config
