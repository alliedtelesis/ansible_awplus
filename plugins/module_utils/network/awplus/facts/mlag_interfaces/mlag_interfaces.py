#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus mlag_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.mlag_interfaces.mlag_interfaces import Mlag_interfacesArgs


class Mlag_interfacesFacts(object):
    """ The awplus mlag_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Mlag_interfacesArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    # Needs to be mockable for unit tests.
    @staticmethod
    def get_run_mlag_interfaces(connection):
        return connection.get("show running-config interface")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for mlag_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            # Normal situation should be no data. Since we need data
            # from multiple sources, it's probably best if we just ignore
            # any data passed in.
            data = self.get_run_mlag_interfaces(connection)

        resources = data.split('!')

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.extend(obj)

        ansible_facts['ansible_network_resources'].pop('mlag_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['mlag_interfaces'] = params['config']

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
        interfaces = []
        # get a list of non-empty lines
        lines = [line for line in conf.splitlines() if line]
        interface_match = re.match(r'interface po(\d+)(?:-(\d+))?', lines[0])
        if not interface_match:
            return

        aggregate_ports = []
        if interface_match[2]:
            aggregate_ports = range(int(interface_match[1]), int(interface_match[2]) + 1)
        else:
            aggregate_ports = [interface_match[1]]

        domain = None
        for line in lines[1:]:
            match = re.match(r' *mlag (\d+)', line)
            if match:
                domain = match.group(1)

        for aggregate_port in aggregate_ports:
            config = deepcopy(spec)
            config['name'] = f"po{aggregate_port}"
            config['domain_id'] = domain
            interfaces.append(config)
        return interfaces
