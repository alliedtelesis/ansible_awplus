#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_lacp class
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


class Lacp(ConfigBase):
    """
    The awplus_lacp class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'lacp',
    ]

    def __init__(self, module):
        super(Lacp, self).__init__(module)

    def get_lacp_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        lacp_facts = facts['ansible_network_resources'].get('lacp')
        if not lacp_facts:
            return {}
        return lacp_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        commands = list()

        existing_lacp_facts = self.get_lacp_facts()
        commands.extend(self.set_config(existing_lacp_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_lacp_facts = self.get_lacp_facts()

        result['before'] = existing_lacp_facts
        if result['changed']:
            result['after'] = changed_lacp_facts

        return result

    def set_config(self, existing_lacp_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_lacp_facts
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
        if want is None or want.get("system").get("priority") is None and want.get("system").get("global_passive_mode") is None:
            self._module.fail_json(
                msg=f"one of 'priority' or 'global_passive_mode' is required.")

        state = self._module.params['state']
        if state in ('merged') and not want:
            self._module.fail_json(msg=f"value of config parameter must not be empty for state {state}")

        if state == 'deleted':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_deleted(**kwargs)
        elif state == 'merged':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_merged(**kwargs)
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
        commands.extend(self._clear_config(want, have))
        return commands

    def _set_config(self, want, have):
        # Set the interface config based on the want and have config
        commands = []
        want, have = want.get("system"), have.get("system")

        priority = want.get('priority')
        if priority and have.get('priority', 32768) != want.get('priority'):
            if self.is_valid_priority(priority):
                cmd = f"lacp system-priority {priority}"
            else:
                self._module.fail_json(msg='Invalid system priority')
            commands.append(cmd)

        gpm = want.get('global_passive_mode')
        if gpm is not None and have.get('global_passive_mode', False) != want.get('global_passive_mode'):
            if gpm is True:
                cmd = "lacp global-passive-mode enable"
            else:
                cmd = "no lacp global-passive-mode enable"
            commands.append(cmd)

        return commands

    def _clear_config(self, want, have):
        # Delete the interface config based on the want and have config
        commands = []

        have_system_priority = have.get('system').get('priority')
        if want.get('system').get('priority') and have_system_priority and have_system_priority != 32768:
            cmd = 'no lacp system-priority'
            commands.append(cmd)

        have_gpm = have.get('system').get('global_passive_mode')
        if want.get('system').get('global_passive_mode') and have_gpm is True:
            cmd = "no lacp global-passive-mode enable"
            commands.append(cmd)

        return commands

    def is_valid_priority(self, priority):
        return 1 <= priority <= 65535
