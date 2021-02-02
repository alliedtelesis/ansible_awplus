#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_interfaces class
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


class Interfaces(ConfigBase):
    """
    The awplus_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'interfaces',
    ]

    def __init__(self, module):
        super(Interfaces, self).__init__(module)

    def get_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        interfaces_facts = facts['ansible_network_resources'].get('interfaces')
        if not interfaces_facts:
            return []
        return interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_interfaces_facts = self.get_interfaces_facts()
        commands.extend(self.set_config(existing_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_interfaces_facts = self.get_interfaces_facts()

        result['before'] = existing_interfaces_facts
        if result['changed']:
            result['after'] = changed_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_interfaces_facts
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

        # p = []
        # for c in commands:
        #     p.append('# %s' % c)
        # return p

        return commands

    @staticmethod
    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        for name, value in iteritems(want):
            if name in have:
                to_clear = dict_diff(value, have[name])
                commands.extend(_clear_config(name, to_clear))
                to_set = dict_diff(have[name], value)
                commands.extend(_set_config(name, to_set))
        return remove_duplicate_interface(commands)

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        commands.extend(self._state_replaced(self, want, have))
        for name, value in iteritems(have):
            if name not in want:
                commands.extend(_clear_config(name, value))
        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        diff = dict_diff(have, want)
        for name, value in iteritems(diff):
            if name in have:
                commands.extend(_set_config(name, value))
        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        if want:
            for name, value in iteritems(want):
                if name in have:
                    commands.extend(_clear_config(name, have[name]))
        else:
            for name, value in iteritems(have):
                commands.extend(_clear_config(name, value))
        return commands


def _set_config(name, value):
    commands = []
    if value.get('description'):
        commands.append('description {}'.format(value['description']))
    if value.get('speed'):
        commands.append('speed {}'.format(value['speed']))
    if value.get('mtu'):
        commands.append('mtu {}'.format(value['mtu']))
    if value.get('duplex'):
        commands.append('duplex {}'.format(value['duplex']))
    if value.get('enabled') is True:
        commands.append('no shutdown')
    elif value.get('enabled') is False:
        commands.append('shutdown')
    if commands:
        commands.insert(0, 'interface {}'.format(name))
    return commands


def _clear_config(name, value):
    commands = []
    if value.get('description'):
        commands.append('no description')
    if value.get('speed'):
        commands.append('no speed')
    if value.get('mtu'):
        commands.append('no mtu')
    if value.get('duplex'):
        commands.append('no duplex')
    if value.get('enabled') is False:
        commands.append('no shutdown')
    if commands:
        commands.insert(0, 'interface {}'.format(name))
    return commands
