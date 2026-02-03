#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus l3_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.l3_interfaces.l3_interfaces import L3_interfacesArgs


class L3_interfacesFacts(object):
    """ The awplus l3_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = L3_interfacesArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_device_data(self, connection):
        return connection.get('show running-config')

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for l3_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_device_data(connection)

        resources = data.split("!")

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('l3_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['l3_interfaces'] = []
            for cfg in params['config']:
                facts['l3_interfaces'].append(utils.remove_empties(cfg))

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
        lines = conf.split('\n')
        lines = [line for line in lines if line]

        if lines and lines[0].startswith('interface vlan'):
            config['name'] = re.match(r'interface (\S+)', lines[0]).group(1)
            ipv4 = list()
            ipv6 = list()
            vrf = None
            for line in lines[1:]:
                # populate ipv4 facts
                each_ipv4 = dict()
                ipv4_match = re.match(r' *ip address (\S+) ?(\S+)?', line)
                if ipv4_match:
                    each_ipv4['address'] = ipv4_match.group(1)
                    if ipv4_match.group(2) == 'secondary':
                        each_ipv4['secondary'] = True
                dhcp_match = re.match(r' *ip dhcp ?client-id (\S+)? ?hostname (\S+)?', line)
                if dhcp_match:
                    each_ipv4['address'] = 'dhcp'
                    each_ipv4['dhcp_client'] = dhcp_match.group(1)
                    each_ipv4['dhcp_hostname'] = dhcp_match.group(2)
                if each_ipv4:
                    ipv4.append(each_ipv4)

                # populate ipv6 facts
                each_ipv6 = dict()
                ipv6_match = re.match(r' *ipv6 address (\S+)', line)
                if ipv6_match:
                    each_ipv6['address'] = ipv6_match.group(1)
                if each_ipv6:
                    ipv6.append(each_ipv6)

                vrf_match = re.match(r' *ip vrf forwarding (\S+)', line)
                if vrf_match:
                    vrf = vrf_match.group(1)
            config['ipv4'] = ipv4
            config['ipv6'] = ipv6
            config['vrf'] = vrf
        return utils.remove_empties(config)
