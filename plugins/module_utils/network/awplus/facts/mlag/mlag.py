#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus mlag fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.mlag.mlag import MlagArgs


class MlagFacts(object):
    """ The awplus mlag fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = MlagArgs.argument_spec
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
    def get_run_mlag(connection):
        return connection.get("show running-config")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for mlag
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
            data = self.get_run_mlag(connection)

        resources = data.split('!')

        obj = {}
        for resource in resources:
            resource = [t for t in resource.splitlines() if t]
            if len(resource) > 0 and "mlag domain" in resource[0]:
                obj = self.render_config(self.generated_spec, resource)

        ansible_facts['ansible_network_resources'].pop('mlag', None)
        facts = {}
        if obj:
            params = utils.validate_config(self.argument_spec, {'config': obj})
            facts['mlag'] = params['config']

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
        domain = re.search(r'mlag domain (\d+)', conf[0]).group(1)
        config["domain"] = domain

        for line in conf[1:]:
            match = re.search(r'source-address (\S+)', line)
            if match:
                config["source_address"] = match.group(1)
                continue

            match = re.search(r'peer-address (\S+)', line)
            if match:
                config["peer_address"] = match.group(1)
                continue

            match = re.search(r'peer-link (\S+)', line)
            if match:
                config["peer_link"] = match.group(1)
                continue

            match = re.search(r'keepalive-interval (\S+)', line)
            if match:
                config["keepalive_interval"] = match.group(1)
                continue
        
            match = re.search(r'session-timeout (\S+)', line)
            if match:
                config["session_timeout"] = match.group(1)
                continue
        return utils.remove_empties(config)

