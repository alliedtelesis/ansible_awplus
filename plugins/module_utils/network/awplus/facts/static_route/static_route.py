#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus static_route fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.static_route.static_route import Static_routeArgs


class Static_routeFacts(object):
    """ The awplus static_route fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Static_routeArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_static_route_conf(self, connection):
        return connection.get("show running-config | include route")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for static_route
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            # typically data is populated from the current device configuration
            # data = connection.get('show running-config | section ^interface')
            # using mock data instead
            data = self.get_static_route_conf(connection)

        resources = re.findall(r'(ip|ipv6) route (.+)', data)

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('static_route', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['static_route'] = params['config']

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
        index = 0

        config['afi'] = 'IPv6' if conf[0] == 'ipv6' else 'IPv4'

        # All valid patterns to match input against
        patterns = [
            ('SADR', r'(\S+) (\S+) (\S+) (\d+) description (.+)'),
            ('SADR', r'(\S+) (\S+) (\S+) (\d+)'),
            ('VRF', r'vrf (\S+) (\S+) (\S+) (\d+) description (.+)'),
            ('VRF', r'vrf (\S+) (\S+) (\S+) (\d+)'),
            ('VRF', r'vrf (\S+) (\S+) (\S+) description (.+)'),
            ('VRF', r'vrf (\S+) (\S+) (\S+)'),
            ('DEFAULT', r'(\S+) (\S+) (\d+) description (.+)'),
            ('SADR', r'(\S+) (\S+) (\S+) description (.+)'),
            ('DEFAULT', r'(\S+) (\S+) (\d+)'),
            ('DEFAULT', r'(\S+) (\S+) description (.+)'),
            ('SADR', r'(\S+) (\S+) (\S+)'),
            ('DEFAULT', r'(\S+) (\S+)'),
        ]

        # iterate through the patterns to find a match
        for pattern in patterns:
            match = re.findall(pattern[1], conf[1])
            if match:
                matched_type = pattern[0]
                break

        if match:
            items = match[0]
            if re.search(r'vrf', conf[1]):
                config['vrf'] = items[0]
                index = 1

            config['address'] = items[0 + index]
            config['next_hop'] = items[1 + index] if matched_type != 'SADR' else items[2]
            config['next_hop'] = config['next_hop'].replace("null", "NULL")
            if config['afi'] == 'IPv6':
                config['source_address'] = items[1] if matched_type == 'SADR' else None

            if matched_type == 'SADR':
                index = 1

            if len(items) > 2 + index:
                if items[2 + index].isnumeric():
                    config['admin_distance'] = items[2 + index]
                if not items[-1].isnumeric():
                    config['description'] = items[-1]

        return utils.remove_empties(config)
