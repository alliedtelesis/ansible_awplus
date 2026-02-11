#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_mlag_interfaces class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""
import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base import (
    ConfigBase,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts


class Mlag_interfaces(ConfigBase):
    """
    The awplus_mlag_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'mlag_interfaces',
    ]

    def __init__(self, module):
        super(Mlag_interfaces, self).__init__(module)

    def get_mlag_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        mlag_interfaces_facts = facts['ansible_network_resources'].get('mlag_interfaces')
        if not mlag_interfaces_facts:
            return []
        return mlag_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        commands = list()

        existing_mlag_interfaces_facts = self.get_mlag_interfaces_facts()
        commands.extend(self.set_config(existing_mlag_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_mlag_interfaces_facts = self.get_mlag_interfaces_facts()

        result['before'] = existing_mlag_interfaces_facts
        if result['changed']:
            result['after'] = changed_mlag_interfaces_facts

        return result

    def set_config(self, existing_mlag_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_mlag_interfaces_facts
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
        if not want and state in ('merged', 'deleted'):
            self._module.fail_json("Config cannot be empty for 'merged' and 'deleted' states.")

        if want:
            for w_interface in want:
                # check that interface given is an aggregate port
                port_name = w_interface['name']
                aggregate_port = re.match(r"po(\d+)", port_name)
                if not aggregate_port:
                    self._module.fail_json("Interface name given is not an aggregate port.")

                # check that the interface given exists
                if state != 'deleted':
                    exists = False
                    for h_interface in have:
                        if port_name == h_interface['name']:
                            exists = True
                    if not exists:
                        self._module.fail_json("Interface name does not exist.")

        if state == 'overridden':
            commands = self._state_overridden(want, have)
        elif state == 'deleted':
            commands = self._state_deleted(want, have)
        elif state == 'merged':
            commands = self._state_merged(want, have)
        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        remove_list = []
        add_list = []
        for h_interface in have:
            match = False
            if want:
                for w_interface in want:
                    if h_interface['name'] == w_interface['name']:
                        match = True
            if not match and h_interface['domain_id']:
                remove_list.append(h_interface)

        for h_interface in have:
            if want:
                for w_interface in want:
                    if h_interface['name'] == w_interface['name']:
                        if not h_interface['domain_id']:
                            add_list.append(w_interface)
                        elif h_interface['domain_id'] != w_interface['domain_id']:
                            remove_list.append(h_interface)
                            add_list.append(w_interface)

        interfaces = {d['name'] for d in add_list} | {d['name'] for d in remove_list}
        for interface in interfaces:
            commands.extend(self._generate_commands(interface, add=add_list, remove=remove_list))
        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        remove_list = []
        add_list = []
        for h_interface in have:
            for w_interface in want:
                if h_interface['name'] == w_interface['name']:
                    if h_interface['domain_id'] != w_interface['domain_id']:
                        if h_interface['domain_id'] is None:
                            add_list.append(w_interface)
                        else:
                            remove_list.append(h_interface)
                            add_list.append(w_interface)

        interfaces = {d['name'] for d in add_list} | {d['name'] for d in remove_list}
        for interface in interfaces:
            commands.extend(self._generate_commands(interface, add=add_list, remove=remove_list))
        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        remove_list = []
        for h_interface in have:
            for w_interface in want:
                if h_interface['domain_id'] and h_interface['name'] == w_interface['name']:
                    remove_list.append(h_interface)

        interfaces = {d['name'] for d in remove_list}
        for interface in interfaces:
            commands.extend(self._generate_commands(interface, add=[], remove=remove_list))

        return commands

    def _generate_commands(self, interface, add, remove):
        """
        Generates commands for the desired config

        :param interface: the aggregate interface
        :param add: a list of items to add
        :param remove: a list of items to remove
        :rtype: A list
        :returns: the commands necessary to achieve the desired config
        """
        commands = []
        for r in remove:
            if interface == r['name']:
                commands.append(f"no mlag {r['domain_id']}")

        for a in add:
            if interface == a['name']:
                commands.append(f"mlag {a['domain_id']}")

        if commands:
            commands.insert(0, f"interface {interface}")
        return commands
