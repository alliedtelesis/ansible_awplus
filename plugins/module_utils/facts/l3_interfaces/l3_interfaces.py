#
# -*- coding: utf-8 -*-
# Copyright 2020 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus l3_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.argspec.l3_interfaces.l3_interfaces import (
    L3_interfacesArgs,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.utils.utils import (
    get_interface_type,
    normalize_interface,
)


class L3_interfacesFacts(object):
    """ The awplus l3_interfaces fact class
    """

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = L3_interfacesArgs.argument_spec
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
            int_name = re.search(r"^(vlan\d+)", line)
            if int_name:
                interfaces.append(int_name.group(1))
        return interfaces

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for l3_interfaces
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
                obj = self.generate_config_list(self.generated_spec, conf, interfaces)
                if obj:
                    objs.extend(obj)

        if interfaces:  # add interfaces not shown in running-config
            for interface in interfaces:
                obj = self.parse_config(self.generated_spec, "interface " + interface, interface)
                if obj:
                    objs.append(obj)

        facts = {}

        if objs:
            facts["l3_interfaces"] = []
            params = utils.validate_config(self.argument_spec, {"config": objs})
            for cfg in params["config"]:
                facts["l3_interfaces"].append(utils.remove_empties(cfg))
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def generate_config_list(self, spec, conf, interfaces):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        intf_configs = []
        match = re.search(r"interface (\S+)", conf)
        if match:
            intf = match.group(1)
            if get_interface_type(intf) != "vlan":
                return []
            # populate the facts from the configuration
        else:
            return []

        int_range = ""
        if "-" in intf:
            int_range = re.search(r"vlan(\d+)-(\d+)", intf)

            if int_range:
                start = int(int_range.group(1))
                end = int(int_range.group(2))

                for i in range(start, end + 1):
                    interface = "vlan" + str(i)

                    if interface in interfaces:  # check if interface exists
                        # populate the facts from the configuration
                        intf_configs.append(self.parse_config(spec, conf, interface))
                        interfaces.remove(interface)

        else:
            if intf in interfaces:
                interfaces.remove(intf)
            intf_configs.append(self.parse_config(spec, conf, intf))

        return intf_configs

    def parse_config(self, spec, conf, intf):
        config = deepcopy(spec)
        config["name"] = normalize_interface(intf)

        ipv4 = []
        ipv4_all = re.findall(r"ip address (\S+.*)", conf)
        for each in ipv4_all:
            each = each.strip()
            each_ipv4 = dict()
            if "secondary" not in each and "dhcp" not in each:
                each_ipv4["address"] = each
                each_ipv4["secondary"] = False
                each_ipv4["dhcp_client"] = None
                each_ipv4["dhcp_hostname"] = None
            elif "secondary" in each:
                each_ipv4["address"] = each.split(" secondary")[0]
                each_ipv4["secondary"] = True
            elif "dhcp" in each:
                each_ipv4["address"] = "dhcp"
                if "client-id" in each:
                    each_ipv4["dhcp_client"] = int(
                        each.split(" hostname ")[0].split("/")[-1][-1]
                    )
                if "hostname" in each:
                    each_ipv4["dhcp_hostname"] = each.split(" hostname ")[-1]
                if "client-id" in each and each_ipv4["dhcp_client"] is None:
                    each_ipv4["dhcp_client"] = int(each.split("/")[-1])
                if "hostname" in each and not each_ipv4["dhcp_hostname"]:
                    each_ipv4["dhcp_hostname"] = each.split(" hostname ")[-1]
            ipv4.append(each_ipv4)
        config["ipv4"] = ipv4

        # Get the configured IPV6 details
        ipv6 = []
        ipv6_all = re.findall(r"ipv6 address (\S+)", conf)
        for each in ipv6_all:
            each_ipv6 = dict()
            each_ipv6["address"] = each.lower()
            ipv6.append(each_ipv6)
        config["ipv6"] = ipv6

        return utils.remove_empties(config)
