#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_lacp_interfaces class
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
    param_list_to_dict,
    iteritems,
    dict_diff,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    remove_duplicate_interface,
)


class Lacp_interfaces(ConfigBase):
    """
    The awplus_lacp_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'lacp_interfaces',
    ]

    def __init__(self, module):
        super(Lacp_interfaces, self).__init__(module)

    def get_lacp_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        lacp_interfaces_facts = facts['ansible_network_resources'].get('lacp_interfaces')
        if not lacp_interfaces_facts:
            return []
        return lacp_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_lacp_interfaces_facts = self.get_lacp_interfaces_facts()
        commands.extend(self.set_config(existing_lacp_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_lacp_interfaces_facts = self.get_lacp_interfaces_facts()

        result['before'] = existing_lacp_interfaces_facts
        if result['changed']:
            result['after'] = changed_lacp_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_lacp_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_lacp_interfaces_facts
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
        want = param_list_to_dict(want) if want else dict()
        have = param_list_to_dict(have) if have else dict()

        kwargs = {'self': self, 'want': want, 'have': have}

        if state == 'overridden':
            commands = self._state_overridden(**kwargs)
        elif state == 'deleted':
            commands = self._state_deleted(**kwargs)
        elif state == 'merged':
            commands = self._state_merged(**kwargs)
        elif state == 'replaced':
            commands = self._state_replaced(**kwargs)

        return commands

    @staticmethod
    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for name, want_dict in iteritems(want):
            if name in have:
                have_dict = have[name]
                commands.extend(_clear_config(name, want_dict, have_dict))
                commands.extend(_set_config(name, want_dict, have_dict))

        return remove_duplicate_interface(commands)

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for name, have_dict in iteritems(have):
            p_have = {name: have_dict}
            if name in want:
                p_want = {name: want[name]}
                commands.extend(self._state_replaced(self, p_want, p_have))
            else:
                commands.extend(self._state_deleted(self, dict(), p_have))

        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []

        for name, want_dict in iteritems(want):
            if name in have:
                have_dict = have[name]
                commands.extend(_set_config(name, want_dict, have_dict))

        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []

        if not want:
            for name, have_dict in iteritems(have):
                commands.extend(_clear_config(name, dict(), have_dict))
        else:
            for name, want_dict in iteritems(want):
                if name in have:
                    have_dict = have[name]
                    commands.extend(_clear_config(name, dict(), have_dict))

        return commands


def _set_config(name, want, have):
    commands = []

    if want.get('timeout') and have.get('timeout', 'long') != want.get('timeout'):
        commands.append('lacp timeout {}'.format(want['timeout']))

    if want.get('port_priority') and have.get('port_priority', 32768) != want.get('port_priority'):
        commands.append('lacp port-priority {}'.format(want['port_priority']))

    if commands:
        commands.insert(0, 'interface {}'.format(name))

    return commands


def _clear_config(name, want, have):
    commands = []

    if have.get('timeout') and not want.get('timeout'):
        commands.append('lacp timeout long')

    if have.get('port_priority') and not want.get('port_priority'):
        commands.append('no lacp port-priority')

    if commands:
        commands.insert(0, 'interface {}'.format(name))

    return commands
