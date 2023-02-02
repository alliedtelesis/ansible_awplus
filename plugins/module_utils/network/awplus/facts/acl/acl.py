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
        
        # with open("output.txt", "w") as f:
        #     f.write(f"")
        # with open("output.txt", "a") as f:
        #     f.write(f"\nansible_facts")
        # with open("output.txt", "a") as f:
        #     f.write(f"\nansible_facts: {ansible_facts}")
        if connection:  # just for linting purposes, remove
            pass

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
        data = self.get_acl_conf(connection)





        # with open("output.txt", "w") as f:
        #     f.write(f"data: {data}\n\n\n")
        # with open("output.txt", "a") as f:
        #     f.write(f"config: {self.generated_spec}")
        
        config = self.generated_spec
        # config['afi'] = self.render_afi_config(data)
        config['acls'] = self.render_acl_config(data, config["afi"])
        
        # with open("output.txt", "a") as f:
        #     f.write(f"config : {config}")

        config = utils.remove_empties(config)

        ansible_facts['ansible_network_resources'].pop('acl', None)

        facts = {'acl': config}   
        ansible_facts['ansible_network_resources'].update(facts)
        # with open("output.txt", "a") as f:
        #     f.write(f"\nansible_facts: {ansible_facts}")
        return ansible_facts
    
    def render_afi_config(self, data):

        # result = re.search(r'IPv6', data)
        # with open("output.txt", "a") as f:
        #     f.write(f"\nresult {result}")
        
        return 'IPv6' if re.search(r'IPv6', data) else 'IPv4'
        

    def render_ace_config(self, line, acl_type):
        ace = dict()
        action = ''
        protocol = ''
        wild_card_mask_dest = ''
        wild_card_mask_source = ''
        dest = ''
        source = ''
        line = ' '.join(line.split())

        # with open("output.txt", "a") as f:
        #     f.write(f"\ntype{acl_type}")

        if acl_type == "Standard":
            acl_match = re.search(r'(\d+) (permit|deny) (\S+) (\S+)', line)
            if acl_match:
                action = acl_match.group(2)
                source = acl_match.group(3) + ' ' + acl_match.group(4)
                # with open("output.txt", "a") as f:
                #     f.write(f"\nhere {(action, source)}")
                # ace["action"] = action
                # ace["source"] = source
        else:
            acl_match = None
            if re.search(r'(any)', line):
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+)', line) # does 0.0.0.255 for source
            elif not re.search(r'icmp-type', line): 
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) (\S+) (\S+)', line)
            else:
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+) icmp-type (\S+)', line)
                # with open("output.txt", "a") as f:
                #     f.write(f"\n{acl_match}")
            if not acl_match:
                acl_match = re.findall(r'(\d+) (permit|deny) (\S+) (\S+) (\S+)', line)
            if acl_match:
                # with open("output.txt", "a") as f:
                #     f.write(f"\n{acl_match}")
                values = acl_match[0]
                action = values[1]
                protocol = values[2]
                source = values[3]
                wild_card_mask_source = ' ' + values[4] if len(acl_match[0]) != 5 else ''

                if re.search(r'icmp-type', line):
                    dest = values[4]
                    ace["icmp-type"] = values[5]
                else:
                    dest = values[5] if len(acl_match[0]) != 5 else values[4]
                    wild_card_mask_dest = ' ' + values[6] if len(acl_match[0]) == 7 else ''
        
        ace["source_addr"] = source + wild_card_mask_source
        if dest != '':
            ace["destination_addr"] = dest + wild_card_mask_dest
        ace["action"] = action
        if protocol != '':
            ace["protocols"] = protocol 
        
        # with open("output.txt", "a") as f:
        #     f.write(f"\nhere {ace}")
        return ace

    def render_acl_config(self, data, afi):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        acls_unsorted = []
        acls = []
        data = data.split("\n")
        acl = dict()
        for count, line in enumerate(data):
            if re.search(r'(Standard|Extended|Named|Hardware)', line):
                # with open("output.txt", "a") as f:
                #     f.write(f"\nline {line} \ndata {data[-1]}")type
                ace_count = count + 1 if len(data) > 2 else 0
                ace_list = []
                if line is not data[-1]:
                    while (re.search(r'(   )', data[ace_count])):
                        ace_list.append(data[ace_count])
                        if ace_count == len(data) - 1:
                            break
                        else:
                            ace_count += 1
                acls_unsorted.append((line, ace_list))
        # with open("output.txt", "a") as f:
        #     f.write(f"\n{acls_unsorted}")
        for item in acls_unsorted:
            ace_list = []
            type_name = item[0]
            ace = item[1]
            acl = dict()
            
            name_match = re.search(r'(\S+) (IP|IPv6) access list (\d+|\S+)', type_name)
            if name_match:
                # acl["type"] = name_match.group(1) if name_match.group(3).isnumeric() else "Named"
                acl["type"] = name_match.group(1)
                acl["afi"] = 'IPv4' if name_match.group(2) == 'IP' else 'IPv6'
                acl["name"] = name_match.group(3)
                # with open("output.txt", "a") as f:
                #     f.write(f"\n{acl['afi']}")
            for entry in ace:
                # if acl["afi"] is not 'IPv6':
                ace_list.append(self.render_ace_config(entry, acl['type']))
                
            acl["ace"] = ace_list
            acls.append(acl)
        # for t in acls:
        #     with open("output.txt", "a") as f:
        #         f.write(f"\nhere{t}")
        return acls
            # with open("output.txt", "a") as f:
            #     f.write(f"\n{ace_list}")

        # for t in acl_list2:
        #     with open("output.txt", "a") as f:
        #         f.write(f"\n{t}")


   