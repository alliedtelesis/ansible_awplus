#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# utils
import re
from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import is_masklen


def remove_command_from_config_list(interface, cmd, commands):
    # To delete the passed config
    if interface not in commands:
        commands.insert(0, interface)
    commands.append('no %s' % cmd)
    return commands


def add_command_to_config_list(interface, cmd, commands):
    # To set the passed config
    if interface not in commands:
        commands.insert(0, interface)
    commands.append(cmd)


def filter_dict_having_none_value(want, have):
    # Generate dict with have dict value which is None in want dict
    test_dict = dict()
    test_key_dict = dict()
    name = want.get('name')
    if name:
        test_dict['name'] = name
    diff_ip = False
    want_ip = ''
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
                if each.get('secondary'):
                    want_ip = each.get('address').split('/')
                    have_ip = have.get('ipv4')
                    if len(want_ip) > 1 and have_ip and have_ip[0].get('secondary'):
                        have_ip = have_ip[0]['address'].split(' ')[0]
                        if have_ip != want_ip[0]:
                            diff_ip = True
                    if each.get('secondary') and diff_ip is True:
                        test_key_dict.update({'secondary': True})
                    test_dict.update({'ipv4': test_key_dict})
        if v is None:
            val = have.get(k)
            test_dict.update({k: val})
    return test_dict


def remove_duplicate_interface(commands):
    # Remove duplicate interface from commands
    set_cmd = []
    for each in commands:
        if 'interface' in each:
            if each not in set_cmd:
                set_cmd.append(each)
        else:
            set_cmd.append(each)
    return set_cmd


def get_interfaces(want):
    # Get interfaces separated by commas
    if ' ' in want:
        raise ValueError('Interface names and comma-separated names should not have spaces.')
        # self._module.fail_json("Interface names and comma-separated names should not have spaces.")
    if ',' in want:
        intfs = want.split(',')
        int_type = get_interface_type(intfs[0])
        for intf in intfs:
            intf_type = get_interface_type(intf)
            if intf_type == 'unknown':
                raise ValueError('Invalid interface - unknown interface')
                # self._module.fail_json("Invalid interface - unknown interface")
            if int_type != intf_type:
                raise ValueError('Interfaces mismatch, Interfaces in range must be of the same type')
                # self._module.fail_json("Interfaces mismatch, Interfaces in range must be of the same type")
        return intfs
    else:
        return [want]


def get_have_dict(want, have):
    # Determines whether the given interface/s exist
    # returns the configuration of the wanted interface, blank dict for range and none if the interface does not exist
    if want.startswith('port'):
        return get_port_dict(want, have)
    if '-' in want:
        intf_range = re.search(r'([a-z]+)(\d+)-(\d+)', want)
        if intf_range:
            if int(intf_range.group(3)) <= int(intf_range.group(2)):
                raise ValueError('Invalid Input - range end must be greater than range start')
                # self._module.fail_json("Invalid Input - range end must be greater than range start")
            for i in range(int(intf_range.group(2)), int(intf_range.group(3)) + 1):
                for intf in have:  # check if all interfaces in range exists
                    if intf_range.group(1) + str(i) == intf['name']:
                        break
                else:
                    return  # returns none if one of the interfaces does not exist
            return dict()
    else:
        for intf in have:  # check for singular input
            if want == intf['name']:
                return intf
        return


def get_port_dict(want, have):
    # Determines whether the given port/s exist
    # returns the configuration of the wanted port, blank dict for range and none if the port does not exist
    start = want
    end = want
    if '-' in want:
        port = re.search(r'port(\d+).(\d+).(\d+)-(\d+).(\d+).(\d+)', want)
        if port:
            for i in range(3):  # check if valid range
                if int(port.group(i + 1)) > int(port.group(i + 4)):
                    raise ValueError('Invalid Input - range end must be greater than range start')
                    # self._module.fail_json("Invalid Input - range end must be greater than range start")
                elif int(port.group(i + 1)) == int(port.group(i + 4)):
                    continue
                else:
                    break
            else:
                raise ValueError('Invalid Input - range end must be greater than range start')
                # self._module.fail_json("Invalid Input - range end must be greater than range start")
            start = 'port{}.{}.{}'.format(port.group(1), port.group(2), port.group(3))
            end = 'port{}.{}.{}'.format(port.group(4), port.group(5), port.group(6))
    start_exists = False
    end_exists = False
    for intf in have:  # check if port exists
        if start == intf['name']:
            start_exists = True
        if end == intf['name']:
            end_exists = True
        if start == end and start_exists:
            return intf
    if start_exists and end_exists:
        return dict()
    return


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


def int_range_to_list(range_string, int_list):
    """ For a given interface range and list of possible interfaces,
    return a list of the interfaces in the range (as strings).
    :param range_string: interface range as generated by show running-config
    :param int_list: list of valid interface strings (show int brief)
    :rtype: list
    :returns: list of interfaces or None (if errors)
    """
    # Take care of case where we have comma-separated interfaces (use recursion)
    if ',' in range_string:
        ret_list = []
        intranges = range_string.split(',')
        for intrange in intranges:
            sub_list = int_range_to_list(intrange, int_list)
            if sub_list is None:
                return None
            ret_list.extend(sub_list)
        return ret_list

    # Take care of case when it's not a range.
    if '-' not in range_string:
        if range_string in int_list:
            return [range_string]
        else:
            return None

    # It's a range, work out how to expand the range.
    ints = range_string.split('-')
    if len(ints) != 2:
        return None

    # ints[0] is a type and instance, ints[1] is just an instance
    # Find out how many numbers appear in the instance.
    n_inst = 3
    match = re.match(r"([a-z]+)(\d+).(\d+).(\d+)", ints[0], re.I)
    if not match:
        n_inst = 1
        match = re.match(r"([a-z]+)(\d+)", ints[0], re.I)
        if not match:
            return None
    match1 = re.match(r"(\d+).(\d+).(\d+)", ints[1], re.I)
    if match:
        if n_inst != 3:
            return None
    else:
        match1 = re.match(r"(\d+)", ints[1], re.I)
        if not match or n_inst != 1:
            return None

    # Optimise by only allowing the last number to vary.
    # This is how the config comes out.
    ret_list = []
    if n_inst == 3:
        base_name = match.group(1) + match.group(2) + '.' + match.group(3) + '.'
    else:
        base_name = match.group(1)
    for i in range(int(match.group(n_inst + 1)), int(match1.group(n_inst)) + 1):
        int_name = base_name + str(i)
        if int_name in int_list:
            ret_list.append(int_name)
    return ret_list
