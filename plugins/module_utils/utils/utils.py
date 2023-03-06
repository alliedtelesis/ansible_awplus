#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" utils for AW+ networking devices
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible.module_utils.six import iteritems
from ansible.module_utils.common.network import is_masklen, to_netmask


def remove_command_from_config_list(interface, cmd, commands):
    # To delete the passed config
    if interface not in commands:
        commands.insert(0, interface)
    commands.append(f"no {cmd}")
    return commands


def add_command_to_config_list(interface, cmd, commands):
    # To set the passed config
    if interface not in commands:
        commands.insert(0, interface)
    commands.append(cmd)


def dict_to_set(sample_dict):
    # Generate a set with passed dictionary for comparison
    test_dict = dict()
    if isinstance(sample_dict, dict):
        for k, v in iteritems(sample_dict):
            if v is not None:
                if isinstance(v, list):
                    if isinstance(v[0], dict):
                        li = []
                        for each in v:
                            for key, value in iteritems(each):
                                if isinstance(value, list):
                                    each[key] = tuple(value)
                            li.append(tuple(iteritems(each)))
                        v = tuple(li)
                    else:
                        v = tuple(v)
                elif isinstance(v, dict):
                    li = []
                    for key, value in iteritems(v):
                        if isinstance(value, list):
                            v[key] = tuple(value)
                    li.extend(tuple(iteritems(v)))
                    v = tuple(li)
                test_dict.update({k: v})
        return_set = set(tuple(iteritems(test_dict)))
    else:
        return_set = set(sample_dict)
    return return_set


def filter_dict_having_none_value(want, have):
    # Generate dict with have dict value which is None in want dict
    test_dict = dict()
    test_key_dict = dict()
    name = want.get("name")
    if name:
        test_dict["name"] = name
    diff_ip = False
    want_ip = ""
    for k, v in iteritems(want):
        if isinstance(v, dict):
            for key, value in iteritems(v):
                intermediate_dict_val = have.get(k)
                if isinstance(intermediate_dict_val, dict):
                    dict_val = intermediate_dict_val.get(key)
                else:
                    break
                test_key_dict.update({key: dict_val})
            test_dict.update({k: test_key_dict})
        if isinstance(v, list):
            for key, value in iteritems(v[0]):
                if value is None:
                    intermediate_dict_val = have.get(k)
                    if isinstance(intermediate_dict_val, dict):
                        dict_val = intermediate_dict_val.get(key)
                    else:
                        break
                    test_key_dict.update({key: dict_val})
                test_dict.update({k: test_key_dict})
            # below conditions checks are added to check if
            # secondary IP is configured, if yes then delete
            # the already configured IP if want and have IP
            # is different else if it's same no need to delete
            for each in v:
                if each.get("secondary"):
                    want_ip = each.get("address").split("/")
                    have_ip = have.get("ipv4")
                    if len(want_ip) > 1 and have_ip and have_ip[0].get("secondary"):
                        have_ip = have_ip[0]["address"].split(" ")[0]
                        if have_ip != want_ip[0]:
                            diff_ip = True
                    if each.get("secondary") and diff_ip is True:
                        test_key_dict.update({"secondary": True})
                    test_dict.update({"ipv4": test_key_dict})
        if v is None:
            val = have.get(k)
            test_dict.update({k: val})
    return test_dict


def remove_duplicate_interface(commands):
    # Remove duplicate interface from commands
    set_cmd = []
    for each in commands:
        if "interface" in each:
            if each not in set_cmd:
                set_cmd.append(each)
        else:
            set_cmd.append(each)
    return set_cmd


def validate_ipv4(value, module):
    if value:
        address = value.split("/")
        if len(address) != 2:
            module.fail_json(
                msg=f"address format is <ipv4 address>/<mask>, got invalid format {value}"
            )

        if not is_masklen(address[1]):
            module.fail_json(
                msg=f"invalid value for mask: {address[1]}, mask should be in range 0-128"
            )


def validate_ipv6(value, module):
    if value:
        address = value.split("/")
        if len(address) != 2:
            ipv6_addr_config_option = ["autoconfig", "dhcp", "suffix"]
            if value not in ipv6_addr_config_option:
                module.fail_json(
                    msg=f"address format is <ipv6 address>/<mask>, got invalid format {value}"
                )
        else:
            if not 0 <= int(address[1]) <= 128:
                module.fail_json(
                    msg=f"invalid value for mask: {address[1]}, mask should be in range 0-128"
                )


def validate_n_expand_ipv4(module, want):
    # Check if input IPV4 is valid IP and expand IPV4 with its subnet mask
    ip_addr_want = want.get("address")
    if len(ip_addr_want.split(" ")) > 1:
        return ip_addr_want
    validate_ipv4(ip_addr_want, module)
    ip = ip_addr_want.split("/")
    if len(ip) == 2:
        ip_addr_want = f"{ip[0]} {to_netmask(ip[1])}"

    return ip_addr_want


def normalize_interface(name):
    """Return the normalized interface name
    """
    if not name:
        return

    def _get_number(name):
        digits = ""
        for char in name:
            if char.isdigit() or char in "/.-":
                digits += char
        return digits

    if name.lower().startswith("et"):
        if_type = "eth"
    elif name.lower().startswith("vl"):
        if_type = "vlan"
    elif name.lower().startswith("lo"):
        if_type = "lo"
    elif name.lower().startswith("por"):
        if_type = "port"
    elif name.lower().startswith("po"):
        if_type = "po"
    elif name.lower().startswith("sa"):
        if_type = "sa"
    elif name.lower().startswith("br"):
        if_type = "br"
    elif name.lower().startswith("of"):
        if_type = "of"
    elif name.lower().startswith("tu"):
        if_type = "tunnel"
    else:
        if re.search(r"(\d+\.\d+\.\d+)", name):
            if_type = "port"
        else:
            if_type = None

    number_list = name.split(" ")
    if len(number_list) == 2:
        number = number_list[-1].strip()
    else:
        number = _get_number(name)

    if if_type:
        proper_interface = if_type + number
    else:
        proper_interface = name

    return proper_interface


def get_interface_type(interface):
    """Gets the type of interface
    """

    if interface.upper().startswith("ET"):
        return "ethernet"
    elif interface.upper().startswith("VL"):
        return "vlan"
    elif interface.upper().startswith("LO"):
        return "loopback"
    elif interface.upper().startswith("POR"):
        return "port"
    elif interface.upper().startswith("PO"):
        return "dynamic aggregator"
    elif interface.upper().startswith("SA"):
        return "static aggregator"
    elif interface.upper().startswith("BR"):
        return "bridge"
    elif interface.upper().startswith("OF"):
        return "openflow"
    elif interface.upper().startswith("TU"):
        return "tunnel"
    else:
        if re.search(r"(\d+\.\d+\.\d+)", interface):
            return "port"
        return "unknown"


def get_sys_info(data):
    """
    Pass in the output of 'show system', return a dictionary with
    'model' and 'serialnum'
    """
    for ss_line in data.splitlines():
        s_data = ss_line.strip()
        extra_field = False
        match = re.search(
            r"^Base\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$", s_data, re.M
        )
        if not match:
            extra_field = True
            match = re.search(
                r"^Base\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$", s_data, re.M
            )
        if match:
            if extra_field:
                return {"model": match.group(3) + " " + match.group(4), "serialnum": match.group(6)}
            else:
                return {"model": match.group(3), "serialnum": match.group(5)}
    return {"model": "--unknown--", "serialnum": "--unknown--"}
