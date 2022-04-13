#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus logging fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.logging.logging import LoggingArgs


class LoggingFacts(object):
    """ The awplus logging fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = LoggingArgs.argument_spec
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
        return connection.get('show running-config | include log')

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for logging
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """

        if not data:
            # typically data is populated from the current device configuration
            data = self.get_run_conf(connection)

        resources = data.split('\n')
        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('logging', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['logging'] = [utils.remove_empties(cfg) for cfg in params['config']]

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

        log = utils.parse_conf_arg(conf, 'log')
        config['dest'] = log.split()[0] if log else None
        if not config['dest']:
            return
        if config['dest'] == 'host':
            host = utils.parse_conf_arg(conf, 'host')
            config['name'] = host.split()[0] if host else None

        size = utils.parse_conf_arg(conf, 'size')
        config['size'] = size.split()[0] if size else None

        facility = utils.parse_conf_arg(conf, 'facility')
        config['facility'] = facility.split()[0] if facility else None

        level = utils.parse_conf_arg(conf, 'level')
        config['level'] = level.split()[0] if level else None

        return utils.remove_empties(config)
