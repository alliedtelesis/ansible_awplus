#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus vrfs fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.vrfs.vrfs import VrfsArgs


class VrfsFacts(object):
    """ The awplus vrfs fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = VrfsArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_data(self, connection):
        return connection.get('show running-config')

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for vrfs
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_data(connection)

        # split the config into instances of the resource
        objs = []
        for resource in data.split('!'):
            if resource and resource.lstrip().startswith('ip vrf'):
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('vrfs', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['vrfs'] = params['config']

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

        for conf_line in conf.splitlines():
            ls = conf_line.strip()
            if ls.startswith('ip vrf'):
                match = re.search(r'ip vrf (\S+) (\d+)', ls)
                if match:
                    config['name'] = match.group(1)
                    config['id'] = match.group(2)
            elif ls.startswith('description'):
                config['description'] = ls[len('description '):]
            elif ls.startswith('max-static-routes'):
                match = re.search(r'max-static-routes (\d+)', ls)
                if match:
                    config['max_static_routes'] = match.group(1)
            elif ls.startswith('max-fib-routes'):
                match = re.search(r'max-fib-routes (\d+)( \S+)?', ls)
                if match:
                    config['max_fib_routes'] = match.group(1)
                    config['max_fib_routes_warning'] = match.group(2)[1:] if match.group(2) else None
            elif ls.startswith('rd'):
                config['rd'] = ls[len('rd '):]
            elif ls.startswith('import map'):
                config['import_map'] = ls[len('import map '):]
            elif ls.startswith('export map'):
                config['export_map'] = ls[len('export map '):]
            elif ls.startswith('router-id'):
                config['router_id'] = ls[len('router-id '):]
            elif ls.startswith('route-target'):
                match = re.search(r'route-target (import|export|both) (\S+)', ls)
                if match:
                    new_rt = {'target': match.group(2), 'direction': match.group(1)}
                    if config['route_target'] is None:
                        config['route_target'] = [new_rt]
                    else:
                        config['route_target'].append(new_rt)

        return utils.remove_empties(config)
