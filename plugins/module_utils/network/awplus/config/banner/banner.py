#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_banner class
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
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts


class Banner(ConfigBase):
    """
    The awplus_banner class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'banner',
    ]

    def __init__(self, module):
        super(Banner, self).__init__(module)

    def get_banner_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        banner_facts = facts['ansible_network_resources'].get('banner')
        if not banner_facts:
            return {}
        return banner_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_banner_facts = self.get_banner_facts()
        commands.extend(self.set_config(existing_banner_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_banner_facts = self.get_banner_facts()

        result['before'] = existing_banner_facts
        if result['changed']:
            result['after'] = changed_banner_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_banner_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_banner_facts
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

        want = param_list_to_dict(want, unique_key='banner') if want else dict()
        have = param_list_to_dict(have, unique_key='banner') if have else dict()

        if state == 'deleted':
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

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for name, want_dict in iteritems(want):
            kwargs = {'self': self, 'want': {name: want[name]}, 'have': have}
            commands.extend(self._state_merged(**kwargs))

        for name, have_dict in iteritems(have):
            if name not in want:
                commands.extend(_clear_config(name))

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
            if want_dict != have.get(name):
                commands.extend(_set_config(name, want_dict, self._module))

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
                commands.extend(_clear_config(name))
        else:
            for name, want_dict in iteritems(want):
                if name in have:
                    commands.extend(_clear_config(name))

        return commands


def _clear_config(name):
    commands = []

    if name == 'motd':
        commands.append('no banner motd')
    elif name == 'exec':
        commands.append('banner exec default')

    return commands


def _set_config(name, want, module):
    commands = []

    if not want.get('text'):
        module.fail_json('Text is required.')

    commands.append(f"banner {name} {want['text']}")

    return commands
