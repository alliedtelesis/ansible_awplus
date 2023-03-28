#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus premark_dscps fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.premark_dscps.premark_dscps import Premark_dscpsArgs


class Premark_dscpsFacts(object):
    """ The awplus premark_dscps fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Premark_dscpsArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_premark_dscps_conf(self, connection):
        return connection.get("show mls qos maps premark-dscp")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for premark_dscps
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if connection:  # just for linting purposes, remove
            pass

        if not data:
            data = self.get_premark_dscps_conf(connection)
        resources = data.split('\n\n')

        objs = []
        for resource in resources:
            if resource:
                obj = self.render_config(self.generated_spec, resource)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('premark_dscps', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['premark_dscps'] = params['config']

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
        dscp_match = re.search(r'DSCP (\d+)', conf)
        if dscp_match:
            config['dscp_in'] = dscp_match.group(1)

        new_dscp_match = re.search(r'New DSCP               (\d+)', conf)
        if new_dscp_match:
            config['dscp_new'] = new_dscp_match.group(1)

        new_cos_match = re.search(r'New CoS                (\d+)', conf)
        if new_cos_match:
            config['cos_new'] = new_cos_match.group(1)

        new_class_match = re.search(r'New Bandwidth Class    (green|yellow|red)', conf)
        if new_class_match:
            config['class_new'] = new_class_match.group(1)

        return utils.remove_empties(config)
