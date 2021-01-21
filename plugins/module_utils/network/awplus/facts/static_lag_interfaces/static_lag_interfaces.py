#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus static_lag_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.static_lag_interfaces.static_lag_interfaces import (
    Static_lag_interfacesArgs
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    int_range_to_list
)


class Static_lag_interfacesFacts(object):
    """ The awplus static_lag_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Static_lag_interfacesArgs.argument_spec
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
    def get_run_conf(self, connection):
        return connection.get("show running-config interface")

    # Needs to be mockable for unit tests.
    def get_int_brief(self, connection):
        int_brief = connection.get("show interface brief").splitlines()
        return [i.split()[0].strip() for i in int_brief][1:]

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for static_lag_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_run_conf(connection)
        int_list = self.get_int_brief(connection)

        # split the config into instances of the resource
        objs = []
        config = data.split("!")
        for conf in config:
            obj = self.render_config(self.generated_spec, conf, int_list)
            if obj:
                objs.append(obj)

        # merge list of dictionaries as a dictionary indexed by name
        merge_dict = {}
        for obj in objs:
            if obj["name"] not in merge_dict:
                merge_dict[obj["name"]] = obj
            else:
                merge_dict[obj["name"]]["members"].extend(obj["members"])
        objs = list(merge_dict.values())

        ansible_facts['ansible_network_resources'].pop('static_lag_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['static_lag_interfaces'] = params['config']

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf, int_list):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :param int_list: List of all interfaces.
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)

        # Only for interfaces with channel-group embedded in it.
        channel_group = re.search(r"static-channel-group (\d+)( member-filters)?", conf)
        if not channel_group:
            return None

        # Get interface range
        match = re.search(r"interface (\S+)", conf)
        if not match:
            return None

        if not match.group(1).startswith("port"):
            return None

        interfaces = int_range_to_list(match.group(1), int_list)
        config["name"] = channel_group.group(1)
        config["member-filters"] = True if channel_group.group(2) else False
        config["members"] = []
        for interface in interfaces:
            config["members"].append(interface)

        return utils.remove_empties(config)
