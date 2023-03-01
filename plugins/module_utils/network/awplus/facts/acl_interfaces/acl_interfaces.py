#
# -*- coding: utf-8 -*-
# Allied Telesis Copyright 2023
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus acl_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.acl_interfaces.acl_interfaces import Acl_interfacesArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    int_range_to_list
)


class Acl_interfacesFacts(object):
    """ The awplus acl_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Acl_interfacesArgs.argument_spec
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
    def get_running_config(connection):
        return connection.get("show running-config interface")

    @staticmethod
    def get_port_list(connection):
        return connection.get("show interface brief")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for acl_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_running_config(connection)
        int_brief = self.get_port_list(connection)
        int_brief = int_brief.splitlines()
        int_list = [i.split()[0].strip() for i in int_brief][1:]

        # split the config into instances of the resource
        objs = []
        config = data.split("!")
        for conf in config:
            partial_objs = self.render_config(self.generated_spec, conf, int_list)
            if partial_objs:
                objs.append(partial_objs[0])

        ansible_facts['ansible_network_resources'].pop('acl_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['acl_interfaces'] = params['config']

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf, int_list):
        """
        Render config as array structure of dictionaries
        and remove empties from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :param int_list: List of all interfaces.
        :rtype: dictionary
        :returns: The generated config
        """
        objs = []
        # Only for interfaces with access-groups embedded in it.
        acls = re.findall(r"access-group ([a-zA-Z0-9-_.]+)", conf)
        if acls == []:
            return None
        # Get interface range
        match = re.search(r"interface ([a-zA-Z0-9._-]+)", conf)
        if not match:
            return None

        if not match.group(1).startswith("port"):
            return None

        interfaces = int_range_to_list(match.group(1), int_list)

        for interface in interfaces:
            config = deepcopy(spec)
            config["name"] = interface
            config["acl_names"] = acls
            objs.append(utils.remove_empties(config))
        return objs
