#
# -*- coding: utf-8 -*-
# Allied Telesis Copyright 2023
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_acl_interfaces class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base import (
    ConfigBase,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts
import re


class Acl_interfaces(ConfigBase):
    """
    The awplus_acl_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'acl_interfaces',
    ]

    def __init__(self, module):
        super(Acl_interfaces, self).__init__(module)

    def get_acl_interfaces_facts(self):

        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        acl_interfaces_facts = facts['ansible_network_resources'].get('acl_interfaces')
        if not acl_interfaces_facts:
            return []
        return acl_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_acl_interfaces_facts = self.get_acl_interfaces_facts()
        commands.extend(self.set_config(existing_acl_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_acl_interfaces_facts = self.get_acl_interfaces_facts()

        result['before'] = existing_acl_interfaces_facts
        if result['changed']:
            result['after'] = changed_acl_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_acl_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_acl_interfaces_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        state = self._module.params['state']
        if state == 'overridden':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_overridden(**kwargs)
        elif state == 'deleted':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_deleted(**kwargs)
        elif state == 'merged':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_merged(**kwargs)
        elif state == 'replaced':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_replaced(**kwargs)

        return commands

    @staticmethod
    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        Function deletes access-group for an interface in have if not in want
          - "If access_group in have and want -> replace access_group in have with that in want"

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        want_interfaces = dict()
        if want is not None:
            want_interfaces = self.get_structure_info(want)
        have_interfaces = self.get_structure_info(have)

        # iterate through interfaces both in want and have
        for interface in list(set(have_interfaces.keys()).intersection(set(want_interfaces.keys()))):
            have_interfaces_set = set(have_interfaces[interface])
            want_interfaces_set = set(want_interfaces[interface])

            removed_access_groups = list(have_interfaces_set - want_interfaces_set)  # acls in have but not want
            added_access_groups = list(want_interfaces_set - have_interfaces_set)  # acls in want but not have

            # generate commands for adding and removing access-groups
            commands.extend(self.generate_commands(interface, removed_access_groups, True))
            commands.extend(self.generate_commands(interface, added_access_groups, False))

        return commands

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        Function ensures that have and want are identical
          - "Remove anything not in want, add anything not in have"

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want_interfaces = dict()
        commands = []

        if want is not None:
            want_interfaces = self.get_structure_info(want)
        have_interfaces = self.get_structure_info(have)

        # iterates through all interfaces in have but not in want
        for interface in list(set(have_interfaces.keys()).difference(set(want_interfaces.keys()))):
            # Since they are not in want, remove them all
            commands.extend(self.generate_commands(interface, have_interfaces[interface], True))

        # iterates through all interfaces in want but not in have
        for interface in list(set(want_interfaces.keys()).difference(set(have_interfaces.keys()))):
            # Since they are in want but not have, add them all
            commands.extend(self.generate_commands(interface, want_interfaces[interface], False))

        # iterates through all interfaces both in want and have
        for interface in list(set(have_interfaces.keys()).intersection(set(want_interfaces.keys()))):
            # ACls common to both want/have, need specific changes (adding + removing acls)
            have_interfaces_set = set(have_interfaces[interface])
            want_interfaces_set = set(want_interfaces[interface])

            removed_access_groups = list(have_interfaces_set - want_interfaces_set)  # ACls in have but not want (remove)
            added_access_groups = list(want_interfaces_set - have_interfaces_set)  # ACls in want but not have (add)

            # generate commands for adding and removing access-groups
            commands.extend(self.generate_commands(interface, removed_access_groups, True))
            commands.extend(self.generate_commands(interface, added_access_groups, False))
        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        Function adds all access-groups specified in want if they don't exist in have
          - "if not contained in have -> add access-group to interface in have"

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        want_interfaces = dict()
        if want is not None:
            want_interfaces = self.get_structure_info(want)
        have_interfaces = self.get_structure_info(have)

        # iterates through all interfaces in want but not in have
        for interface in list(set(want_interfaces.keys()).difference(set(have_interfaces.keys()))):
            # add access-groups
            commands.extend(self.generate_commands(interface, want_interfaces[interface], False))

        # iterates through all interfaces both in want and have
        for interface in list(set(have_interfaces.keys()).intersection(set(want_interfaces.keys()))):
            # only add access-groups in want but not have
            have_interfaces_set = set(have_interfaces[interface])
            want_interfaces_set = set(want_interfaces[interface])
            added_access_groups = list(want_interfaces_set - have_interfaces_set)
            commands.extend(self.generate_commands(interface, added_access_groups, False))
        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        Function deleted all access-groups specified in want if they exist in have
          - "If in both have and want -> delete from have"

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        want_interfaces = dict()
        if want is not None:
            want_interfaces = self.get_structure_info(want)
        have_interfaces = self.get_structure_info(have)

        # iterates through interfaces both in want and have
        for interface in list(set(have_interfaces.keys()).intersection(set(want_interfaces.keys()))):

            have_interfaces_set = set(have_interfaces[interface])
            want_interfaces_set = set(want_interfaces[interface])

            if want_interfaces_set == set():
                # If no acls specified in want,
                #   - remove all acls attached to said interface in have
                removed_access_groups = have_interfaces[interface]
            else:
                # If access-groups isn't empty, remove only it's specified access-groups
                removed_access_groups = list(have_interfaces_set.intersection(want_interfaces_set))
            commands.extend(self.generate_commands(interface, removed_access_groups, True))
        return commands

    def generate_commands(self, interface_name, access_group_list, is_delete=True):
        """ Generates the required commands to add/remove ACLs from an interface

        :param interface_name: The name of the interface
        :param access_group_list: A list of ACLs to attach to interface
        :param is_delete: Determines whether to remove or add an acl to an interface
        :rtype: A list
        :returns: The commands required to achieve the desired configuration
        """
        commands = []
        if interface_name is not None:
            ADD_ACL_COMMAND = "no access-group" if is_delete else 'access-group'
            for access_group_name in access_group_list:
                commands.append(f"{ADD_ACL_COMMAND} {access_group_name}")
            if len(commands) > 0:
                commands.insert(0, f"interface {interface_name}")
        return commands

    def get_acl(self, name):
        """ Gets the ACL configuration

        :param name: The name of the ACL
        :rtype: string
        :returns: The configuration of the ACL
        """
        connection = self._connection
        return connection.get(f"show access-list {name}")

    def get_structure_info(self, interface_structure_dict):
        """ Creates a dictionary with structure so that want and have can be compared directly

        :param interface_structure_dict: The dictionary structure passed through
        :rtype: A dictionary
        :returns: A dictionary with structure
                  {'port_name_1': [acl_1, acl_2], port_name_2': [acl_1, acl_2]}
        """
        port_info_dictionary = dict()
        if interface_structure_dict != []:
            for config in interface_structure_dict:
                port_name = config.get('name')
                acl_list = config.get('acl_names') if config.get('acl_names') is not None else []
                valid_acls = []
                for acl_name in acl_list:
                    # get the ACL configuration for each name
                    have_acl = self.get_acl(acl_name)
                    # extract the header from the returned ACL
                    acl_header = re.findall(r'(\S+) (IP|IPv6) access list (\d+|\S+)', have_acl)
                    # only want to add acls to list if its a hardware acl
                    if acl_header != [] and 'Hardware' in acl_header[0]:
                        valid_acls.append(acl_name)
                port_info_dictionary[port_name] = valid_acls
        return port_info_dictionary
