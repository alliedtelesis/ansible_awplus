#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
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
        with open("output.txt", "w") as f:
            f.write("")
        if not data:
            # typically data is populated from the current device configuration
            # data = connection.get('show running-config | section ^interface')
            # using mock data instead
            data = ("resource rsrc_a\n"
                    "  a_bool true\n"
                    "  a_string choice_a\n"
                    "  resource here\n"
                    "resource rscrc_b\n"
                    "  key is property01 value is value end\n"
                    "  an_int 10\n")

        # get required information
        data = self.get_acl_conf(connection)

        # render config
        config = self.generated_spec
        config['acls'] = self.render_acl_config(data)

        config = utils.remove_empties(config)

        ansible_facts['ansible_network_resources'].pop('acl', None)

        facts = {'acl': config}
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

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
        dest_port = ''
        dest_port_type = ''
        source = ''
        source_port = ''
        source_port_type = ''
        ICMP_num = ''
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
            with open("output.txt", "a") as f:
                f.write(f"\n{line}\n")
            acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+)', line)
            # ('16', 'deny', 'tcp', '10.40.42.0/24', 'range', '8', '10', '10.50.50.0/24', 'range', '12', '14')
            if not acl_match:
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+)', line)
                # ('20', 'deny', 'tcp', '10.40.42.0/24', 'range', '8', '10', '10.50.50.0/24', 'lt', '12'
                # ('12', 'deny', 'tcp', '10.40.42.0/24', 'eq', '10', '10.50.50.0/24', 'range', '12', '14')
            if not acl_match:
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+)', line)
                # ('8', 'deny', 'udp', '10.40.42.0/24', 'eq', '10', '10.50.50.0/24', 'eq', '12')
            if not acl_match:
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+)', line)
            if not acl_match:
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+) (\S+)', line)
                # ('20', 'deny', 'tcp', '10.50.50.0/24', 'eq', '12', 'any')
                # ('12', 'deny', 'tcp', 'any', '10.50.50.0/24', 'eq', '12')
            if not acl_match:
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+)', line)
                # ('16', 'deny', 'tcp', 'any', 'any')

            # with open("output.txt", "a") as f:
            #     f.write(f"{acl_match}\n")
            
            values = acl_match[0]
            action = values[1]
            protocol = values[2]
            source = values[3]
            if len(values) == 5:
                dest = values[4]
            if len(values) == 7:
                if values[4] not in ('eq', 'lt', 'gt', 'ne'):
                    dest = values[4]
                else:
                    dest = values[6]
                    source_port_type = values[4]
                    source_port = values[5]
            if len(values) == 8:
                pass

                # dest = values[4] if values[4] not in ('eq', 'lt', 'gt', 'ne') else values[6]
                # source_port_type = values[4] if values[4] in ('eq', 'lt', 'gt', 'ne') else
            with open("output.txt", "a") as f:
                f.write(f"{(action, protocol, source, source_port_type, source_port, dest)} {len(values)}\n")
        
        else:
            acl_match = None

            if re.search(r'icmp-type', line):
                # handles icmp acls
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) icmp-type (\d+)', line)
            elif re.search(r'(any)', line):
                # if destination is any
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+)', line)
            else:
                # if destination has address and wild card mask
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+) (\S+)', line)
            if not acl_match:
                # if the address prefix is used for addresses
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+)', line)

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
        if dest != '':
            ace["destination_addr"] = dest + wild_card_mask_dest
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
        acls_unsorted = []
        acls = []
        data = data.split("\n")
        acl = dict()
        for count, line in enumerate(data):
            # look if line is a new acl
            if re.search(r'(Standard|Extended|Named|Hardware)', line):
                ace_count = count + 1 if len(data) > 2 else 0
                ace_list = []
                if line is not data[-1]:
                    # add all aces under acl name to a list
                    while (re.search(r'(   )', data[ace_count])):
                        ace_list.append(data[ace_count])
                        if ace_count == len(data) - 1:
                            break
                        else:
                            ace_count += 1
                acls_unsorted.append((line, ace_list))
        for item in acls_unsorted:
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
            acls.append(acl)
        return acls



# awplus#show access-list
# Standard IP access list 72
#     4 deny   any
# Extended IP access list 104
#     4 permit ip 196.144.88.0 0.0.0.255 any
# Extended IP access list 2001
#     4 deny   ip 170.42.45.0 0.0.0.255 any
#     8 permit ip 141.143.42.0 0.0.0.255 any
#    12 permit ip 181.185.85.0 0.0.0.255 any
#    16 deny   ip 10.201.20.0 0.0.0.255 any
# Named Extended IP access list test
#     4 deny   icmp 192.143.87.0/24 192.142.50.0/24 icmp-type 8
#     8 deny   tcp 10.40.42.0/24 eq 10 10.50.50.0/24 eq 12
#    12 deny   tcp any 10.50.50.0/24 eq 12
#    16 deny   tcp any any
#    20 deny   tcp 10.50.50.0/24 eq 12 any
# Named Extended IPv6 access list ipv6_test
#     4 deny   icmp 2001:db8::/64 2001:db8::f/64
# Hardware IP access list 3000
#     4 deny icmp 192.192.92.0/24 197.197.97.0/24 icmp-type 8
# Hardware IP access list hardware_acl
#     4 permit ip 192.192.92.0/24 any
#     8 deny ip 198.192.92.0/24 any
#    12 deny tcp 10.40.42.0/24 eq 10 10.50.50.0/24 range 12 14
#    16 deny tcp 10.40.42.0/24 range 8 10 10.50.50.0/24 range 12 14
