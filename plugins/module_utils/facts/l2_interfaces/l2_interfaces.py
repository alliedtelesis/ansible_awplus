#
# -*- coding: utf-8 -*-
# Copyright 2020 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus l2_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.argspec.l2_interfaces.l2_interfaces import (
    L2_interfacesArgs,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.utils.utils import (
    get_interface_type,
    normalize_interface,
)


class L2_interfacesFacts(object):
    """ The awplus l2_interfaces fact class
    """

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = L2_interfacesArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_device_data(self, connection):
        return connection.get("show running-config interface")

    def get_interface_brief(self, connection):
        return connection.get("show interface brief")

    def get_interfaces(self, connection):
        interfaces = []
        brief = self.get_interface_brief(connection)
        int_brief = brief.split("\n")
        for line in int_brief:
            int_name = re.search(r"^(\S+)", line)
            if int_name:
                if get_interface_type(int_name.group(1)) != "unknown":
                    interfaces.append(int_name.group(1))
        return interfaces

    def populate_facts(self, connection, ansible_facts, data=None):
        """
        Populate the facts for l2_interfaces

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        objs = []

        if not data:
            data = self.get_device_data(connection)
            interfaces = self.get_interfaces(connection)
        # operate on a collection of resource x
        config = data.split("!")
        for conf in config:
            if conf:
                obj = self.generate_config_dict(conf, interfaces)
                if obj:
                    objs.extend(obj)

        facts = {}
        if objs:
            facts["l2_interfaces"] = []
            params = utils.validate_config(self.argument_spec, {"config": objs})
            for cfg in params["config"]:
                facts["l2_interfaces"].append(utils.remove_empties(cfg))
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def generate_config_dict(self, conf, interfaces):
        """
        Generate a list of config as dict for all existing interfaces

        :param conf: The configuration
        :param interfaces: list of existing interfaces
        :rtype: list
        :returns: The generated configs
        """
        match = re.search(r"interface (\S+)", conf)
        intf = match.group(1)
        intf_configs = []

        if get_interface_type(intf) not in ("port", "dynamic aggregator", "static aggregator"):
            return {}

        int_range = ""
        if "-" in intf:
            if get_interface_type(intf) == "port":
                int_range = re.search(r"port(\d+).(\d+).(\d+)-\d+.\d+.(\d+)", intf)
            elif get_interface_type(intf) in ("dynamic aggregator", "static aggregator"):
                int_range = re.search(r"()([a-z]+)(\d+)-(\d+)", intf)

            if int_range:
                start = int(int_range.group(3))
                end = int(int_range.group(4))

                for i in range(start, end + 1):
                    if get_interface_type(intf) == "port":
                        interface = "port" + int_range.group(1) + "." + int_range.group(2) + "." + str(i)
                    else:
                        interface = int_range.group(2) + str(i)

                    if interface in interfaces:  # check if interface exists
                        # populate the facts from the configuration
                        intf_configs.append(self.parse_config(conf, interface))

        else:
            intf_configs.append(self.parse_config(conf, intf))

        return intf_configs

    def parse_config(self, conf, intf):
        """
        Translate a given config into dictionary and delete keys from spec for null values

        :param conf: The configuration
        :param intf: name of the interface
        :rtype: dict
        :returns: The generated config
        """
        config = deepcopy(self.generated_spec)
        config["name"] = normalize_interface(intf)

        mode = utils.parse_conf_arg(conf, "switchport mode")
        if mode == "access":
            has_access = utils.parse_conf_arg(conf, "switchport access vlan")
            if has_access:
                config["access"] = {"vlan": int(has_access)}
            else:
                config["access"] = {"vlan": 1}

        trunk = dict()
        native_vlan = utils.parse_conf_arg(conf, "native vlan")
        if native_vlan and native_vlan != "none":
            trunk["native_vlan"] = int(native_vlan)
        allowed_vlan = utils.parse_conf_arg(conf, "allowed vlan")
        if allowed_vlan:
            trunk["allowed_vlans"] = allowed_vlan.split(",")
            first_vlan = trunk["allowed_vlans"][0]
            if "add" in first_vlan:
                first_vlan = first_vlan.replace("add ", "")
                trunk["allowed_vlans"][0] = first_vlan
        config["trunk"] = trunk
        return utils.remove_empties(config)
