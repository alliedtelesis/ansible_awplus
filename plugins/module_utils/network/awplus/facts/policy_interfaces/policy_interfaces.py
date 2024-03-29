#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus policy_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.policy_interfaces.policy_interfaces import Policy_interfacesArgs


class Policy_interfacesFacts(object):
    """ The awplus policy_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Policy_interfacesArgs.argument_spec
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
    def get_policy_interfaces_conf(connection):
        return connection.get("show mls qos interface")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for policy_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if connection:  # just for linting purposes, remove
            pass

        if not data:
            # typically data is populated from the current device configuration
            # data = connection.get('show running-config | section ^interface')
            # using mock data instead
            data = self.get_policy_interfaces_conf(connection)

        # split the config into instances of the resource by delim and add the deliminator back into the split string
        delim = 'Interface'
        resources = [delim + item for item in data.split(delim) if item]

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('policy_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['policy_interfaces'] = params['config']

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

        int_name_match = re.search(r'Interface: (\S+)', conf)
        if int_name_match:
            config['int_name'] = int_name_match.group(1)

        pol_name_match = re.search(r'INPUT-POLICY-MAP-NAME: (\S+)', conf)
        if pol_name_match:
            config['policy_name'] = pol_name_match.group(1)

        return utils.remove_empties(config)
