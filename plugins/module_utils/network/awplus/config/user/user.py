#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_user class
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


class User(ConfigBase):
    """
    The awplus_user class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'user',
    ]

    def __init__(self, module):
        super(User, self).__init__(module)

    def get_user_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        user_facts = facts['ansible_network_resources'].get('user')
        if not user_facts:
            return {}
        return user_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_user_facts = self.get_user_facts()
        commands.extend(self.set_config(existing_user_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_user_facts = self.get_user_facts()

        result['before'] = existing_user_facts
        if result['changed']:
            result['after'] = changed_user_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_user_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_user_facts
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
        return commands

    @staticmethod
    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        commands.extend(self._set_config(want, have))
        return commands

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for name, want_dict in iteritems(want):
            kwargs = {'self': self, 'want': {name: want[name]}, 'have': {name: have.get(name, {})}}
            commands.extend(self._state_replaced(**kwargs))

        to_delete = {}
        for name, have_dict in iteritems(have):
            if name not in want and name != 'manager':
                to_delete.update({name: have_dict})
        commands.extend(self._clear_config(to_delete, have))

        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        commands.extend(self._set_config(want, have))
        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        if 'manager' not in have or have['manager']['privilege'] != 15:
            commands.append('username manager privilege 15 password friend')
        if want:
            commands.extend(self._clear_config(want, have))
        else:
            commands.extend(self._clear_config(have, have))
        return commands

    def _set_config(self, want, have):
        # set config
        commands = []
        for name, value in iteritems(want):
            if name not in have and (not value.get('configured_password') and not value.get('hashed_password')):
                self._module.fail_json(msg='Password is required.')
            if value.get('configured_password') and value.get('hashed_password'):
                self._module.fail_json(msg='configured_password and hashed_password are mutually exclusive.')
            privilege = value['privilege'] if value['privilege'] else have.get(name, {}).get('privilege', 1)
            if value.get('configured_password'):
                commands.append(f"username {name} privilege {privilege} password {value['configured_password']}")
            elif value.get('hashed_password'):
                commands.append(f"username {name} privilege {privilege} password 8 {value['hashed_password']}")
            elif privilege != have[name]['privilege']:
                commands.append(f"username {name} privilege {privilege}")
        return commands

    def _clear_config(self, to_delete, have):
        # clear config
        commands = []
        for name, value in iteritems(to_delete):
            if name != 'manager' and name in have:
                commands.append(f"no username {name}")
        return commands
