#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus vxlan fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.vxlan.vxlan import VxlanArgs


class VxlanFacts(object):
    """ The awplus vxlan fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = VxlanArgs.argument_spec
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
    def get_run_vxlan(connection):
        return connection.get("show running-config")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for vxlan
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
            data = self.get_run_vxlan(connection)

        resources = data.split('!')

        obj = {}
        internal_facts = {}
        for resource in resources:
            resource = [t for t in resource.splitlines() if t]
            if len(resource) > 0 and "nvo vxlan" in resource[0]:
                obj, internal_facts = self.render_config(self.generated_spec, resource)
        if not obj:
            obj = dict(l2_vnis=[])

        ansible_facts['ansible_network_resources'].pop('vxlan', None)
        facts = {}
        if obj:
            params = utils.validate_config(self.argument_spec, {'config': obj})
            facts['vxlan'] = params['config']
            facts['vxlan']['internal'] = internal_facts

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
        internal_facts = {}
        config["l2_vnis"] = config["l2_vnis"] if config["l2_vnis"] else []
        for line in conf[1:]:
            match = re.search(r'map-access vlan (\d+) vni (\d+)', line)
            if match:
                l2_vni = dict(vlan=match.group(1), vni=match.group(2))
                config["l2_vnis"] += [l2_vni]
                continue

            match = re.search(r'host-reachability-protocol (\S+)', line)
            if match:
                internal_facts["host_reachability"] = match.group(1)
                continue

            match = re.search(r'source-interface (\S+)', line)
            if match:
                internal_facts["source_interface"] = match.group(1)
                continue

        return utils.remove_empties(config), internal_facts
