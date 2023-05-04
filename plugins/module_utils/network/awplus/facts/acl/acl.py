#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus acl fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.acl.acl import AclArgs


class AclFacts(object):
    """ The awplus acl fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = AclArgs.argument_spec
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
    def get_acl_conf(connection):
        return connection.get("show access-list")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for acl
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            # typically data is populated from the current device configuration
            data = self.get_acl_conf(connection)

        # render config
        config = self.generated_spec
        config['acls'] = self.render_acl_config(data)

        config = utils.remove_empties(config)

        ansible_facts['ansible_network_resources'].pop('acl', None)

        facts = {'acl': config}
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    def render_tcp_udp_config(self, values):
        dest_port_protocol = dict()
        source_port_protocol = dict()
        port_index = []
        dest = ''
        # get relevant port information
        for index in range(len(values)):
            if values[index] in ('eq', 'lt', 'gt', 'ne'):
                port_index.append((values[index], values[index + 1], index))
            if values[index] == 'range':
                port_index.append((values[index], values[index + 1], values[index + 2], index))

        if len(port_index) != 0:
            dest = values[port_index[-1][-1] - 1]
            if len(port_index) == 2:
                dest_port_type = port_index[-1][0]
                if dest_port_type == 'range':
                    dest_port_start = port_index[-1][1]
                    dest_port_end = port_index[-1][2]
                    dest_port_protocol[f'{dest_port_type}'] = {'start': dest_port_start, 'end': dest_port_end}
                else:
                    dest_port = port_index[-1][1]
                    dest_port_protocol[f'{dest_port_type}'] = int(dest_port)

                source_port_type = port_index[0][0]
                if source_port_type == 'range':
                    source_port_start = port_index[0][1]
                    source_port_end = port_index[0][2]
                    source_port_protocol[f'{source_port_type}'] = {'start': source_port_start, 'end': source_port_end}
                else:
                    source_port = port_index[0][1]
                    source_port_protocol[f'{source_port_type}'] = int(source_port)

            else:
                if values[-1] == port_index[0][1]:
                    dest_port_type = port_index[0][0]
                    if dest_port_type == 'range':
                        dest_port_start = port_index[0][1]
                        dest_port_end = port_index[0][2]
                        dest_port_protocol[f'{dest_port_type}'] = {'start': dest_port_start, 'end': dest_port_end}
                    else:
                        dest_port = port_index[0][1]
                        dest_port_protocol[f'{dest_port_type}'] = int(dest_port)
                else:
                    source_port_type = port_index[0][0]

                    if source_port_type == 'range':
                        source_port_start = port_index[0][1]
                        source_port_end = port_index[0][2]
                        source_port_protocol[f'{source_port_type}'] = {'start': source_port_start, 'end': source_port_end}
                    else:
                        source_port = port_index[0][1]
                        source_port_protocol[f'{source_port_type}'] = int(source_port)
        return source_port_protocol, dest_port_protocol, dest

    def render_ace_config(self, line, acl_type):
        """ Populate the facts for aces
        :param line: the ace configuration
        :param acl_type: the type of acl
        :rtype: dictionary
        :returns: ace facts
        """
        ace = dict()
        action = ''
        protocol = ''
        wild_card_mask_dest = ''
        wild_card_mask_source = ''
        dest = ''
        source = ''
        ICMP_num = ''
        dest_port_protocol = dict()
        source_port_protocol = dict()
        line = ' '.join(line.split())

        if acl_type == "Standard":
            acl_match = re.findall(r"(\d+) (deny|permit) (\S+) (\S+)", line)
            if not acl_match:
                acl_match = re.findall(r"(\d+) (deny|permit) (\S+)", line)

            if acl_match:
                values = acl_match[0]
                action = values[1]
                source = values[2] + ' ' + values[3] if len(values) == 4 else values[2]
        elif re.search(r'tcp|udp', line):
            values = line.split(' ')  # Split the ace by the spaces
            action = values[1]
            protocol = values[2]
            source = values[3]
            source_port_protocol, dest_port_protocol, dest = self.render_tcp_udp_config(values)

        else:
            acl_match = None

            if re.search(r'icmp-type', line):
                # handles icmp acls
                acl_match = re.findall(
                    r'(\d+) (permit|deny|copy-to-cpu|copy-to-mirror|send-to-mirror|send-to-cpu) '
                    r'(\S+) (\S+) (\S+) icmp-type (\d+)', line
                )
            elif re.search(r'(any)', line):
                # if destination is any
                acl_match = re.findall(
                    r'(\d+) (permit|deny|copy-to-cpu|copy-to-mirror|send-to-mirror|send-to-cpu) '
                    r'(\S+) (\S+) (\S+) (\S+)', line
                )

            else:
                # if destination has address and wild card mask
                acl_match = re.findall(
                    r'(\d+) (permit|deny|copy-to-cpu|copy-to-mirror|send-to-mirror|send-to-cpu) '
                    r'(\S+) (\S+) (\S+) (\S+) (\S+)', line
                )
            if not acl_match:
                # if the address prefix is used for addresses
                acl_match = re.findall(
                    r'(\d+) (permit|deny|copy-to-cpu|copy-to-mirror|send-to-mirror|send-to-cpu) '
                    r'(\S+) (\S+) (\S+)', line
                )

            if acl_match:
                # assign parameters
                values = acl_match[0]
                action = values[1]
                protocol = values[2]
                source = values[3]

                if re.search(r'icmp-type', line):
                    # assign parameters if icmp-type is found
                    dest = values[4]
                    ICMP_num = values[5]

                else:
                    # assign parameters if icmp-type is not found
                    dest = values[5] if len(acl_match[0]) != 5 else values[4]
                    wild_card_mask_dest = ' ' + values[6] if len(acl_match[0]) == 7 else ''
                    wild_card_mask_source = ' ' + values[4] if len(acl_match[0]) != 5 else ''

        # map parameters to ace dictonary
        ace["source_addr"] = source + wild_card_mask_source
        if source_port_protocol != {}:
            ace["source_port_protocol"] = [source_port_protocol]
        if dest != '':
            ace["destination_addr"] = dest + wild_card_mask_dest
        if dest_port_protocol != {}:
            ace["destination_port_protocol"] = [dest_port_protocol]
        ace["action"] = action
        if protocol != '':
            ace["protocols"] = protocol
        if ICMP_num != '':
            ace["ICMP_type_number"] = int(ICMP_num)
        return ace

    def render_acl_config(self, data):
        """
        Render config as dictionary structure and delete keys
          from spec for null values
        :param data: The devices acl config
        :rtype: list
        :returns: list of acls
        """
        acl_list = []
        acl_facts = []

        # order list into form [[acl_name, [ace1, ace2], [acl_name, [ace1, ace2]]]]
        result = re.split(r'Hardware|Standard|Extended|Named', data)
        if result:
            for item in result:
                ace_list = []
                name = ''
                item = item.split('\n')

                for line in item:
                    if re.search(r'access list', line):
                        name = line
                    elif re.search(r'(   )', line):
                        ace_list.append(line)
                if name != '':
                    acl_list.append([name, ace_list])

        # update ACL names so that acl type is also included
        result = data.split('\n')
        acls_names = []
        for item in result:
            if re.search(r'access list', item):
                acls_names.append(item)

        temp_acl_list = acl_list
        for count, item in enumerate(temp_acl_list):
            for acl_name in acls_names:
                acl_name_match = re.search(r'(\S+) (IP|IPv6) access list (\d+|\S+)', acl_name)

                item_name_match = re.search(r'(IP|IPv6) access list (\d+|\S+)', item[0])
                check_acl_name = acl_name_match.group(3) if acl_name_match else None
                item_name = item_name_match.group(2) if item_name_match else None

                if check_acl_name == item_name and check_acl_name and item_name:
                    acl_list[count][0] = acl_name

        # render each acl
        for item in acl_list:
            ace_list = []
            type_name = item[0]
            ace = item[1]
            acl = dict()

            name_match = re.search(r'(\S+) (IP|IPv6) access list (\d+|\S+)', type_name)
            if name_match:
                # assign parameters
                acl["type"] = name_match.group(1)
                acl["afi"] = 'IPv4' if name_match.group(2) == 'IP' else 'IPv6'
                acl["name"] = name_match.group(3)
            for entry in ace:
                # render each ace in acl
                ace_list.append(self.render_ace_config(entry, acl['type']))

            acl["ace"] = ace_list
            acl_facts.append(acl)
        return acl_facts
