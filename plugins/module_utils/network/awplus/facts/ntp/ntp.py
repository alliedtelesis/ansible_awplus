#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus ntp fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.ntp.ntp import NtpArgs


class NtpFacts(object):
    """ The awplus ntp fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = NtpArgs.argument_spec
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
        return connection.get('show running-config | include ntp')

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for ntp
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

        objs = self.fix_structure(objs)

        ansible_facts['ansible_network_resources'].pop('ntp', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['ntp'] = utils.remove_empties(params['config'])

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
        ntp = utils.parse_conf_arg(conf, 'ntp')
        if ntp:
            ntp = ntp.split()
        else:
            return
        if ntp[0] == 'server':
            config['server'] = ntp[1]
        elif ntp[0] == 'authentication-key':
            config['key_id'] = ntp[1]
            config['key_type'] = ntp[2]
            config['auth_key'] = ntp[3]
        elif ntp[0] == 'source':
            config['source_int'] = ntp[1]
        return utils.remove_empties(config)

    def fix_structure(self, objs):
        server = []
        authentication = []
        source = ''
        for obj in objs:
            if obj.get('server'):
                server.append(obj['server'])
            elif obj.get('key_id'):
                authentication.append(obj)
            elif obj.get('source_int'):
                source = obj['source_int']
        config = {'server': server, 'authentication': authentication, 'source_int': source}
        return config
