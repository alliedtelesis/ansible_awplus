#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_policy_interfaces class
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


class Policy_interfaces(ConfigBase):
    """
    The awplus_policy_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'policy_interfaces',
    ]

    def __init__(self, module):
        super(Policy_interfaces, self).__init__(module)

    def get_policy_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        policy_interfaces_facts = facts['ansible_network_resources'].get('policy_interfaces')
        if not policy_interfaces_facts:
            return []
        return policy_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_policy_interfaces_facts = self.get_policy_interfaces_facts()
        commands.extend(self.set_config(existing_policy_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_policy_interfaces_facts = self.get_policy_interfaces_facts()

        result['before'] = existing_policy_interfaces_facts
        if result['changed']:
            result['after'] = changed_policy_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_policy_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_policy_interfaces_facts
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

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        want = [] if not want else want
        for h_pol_int in have:
            h_int_name = h_pol_int.get('int_name')
            for w_pol_int in want:
                w_int_name = w_pol_int.get('int_name')
                if w_int_name == h_int_name:
                    commands.extend(self.change_config(w_pol_int, h_pol_int, replace=True))
        return commands

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        want = [] if not want else want
        w_ints = [w_pol_int.get('int_name') for w_pol_int in want]
        for h_pol_int in have:
            h_int_name = h_pol_int.get('int_name')
            if h_int_name in w_ints:
                for w_pol_int in want:
                    w_int_name = w_pol_int.get('int_name')
                    if w_int_name == h_int_name:
                        # update entry in have to match want
                        commands.extend(self.change_config(w_pol_int, h_pol_int, replace=True))
            else:
                # have entry does not exist in want so delete
                commands.extend(self.change_config(h_pol_int, h_pol_int, delete=True))
        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        want = [] if not want else want
        for h_pol_int in have:
            h_int_name = h_pol_int.get('int_name')
            for w_pol_int in want:
                w_int_name = w_pol_int.get('int_name')
                if w_int_name == h_int_name:
                    commands.extend(self.change_config(w_pol_int, h_pol_int, merge=True))
        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        want = [] if not want else want
        for h_pol_int in have:
            h_int_name = h_pol_int.get('int_name')
            for w_pol_int in want:
                w_int_name = w_pol_int.get('int_name')
                if w_int_name == h_int_name:
                    commands.extend(self.change_config(w_pol_int, h_pol_int, delete=True))
        return commands

    def change_config(self, w_pol_int, h_pol_int, delete=False, merge=False, replace=False):
        """ Generate commands to change the config, given a state flag
        :param w_pol_int: dictionary of the policy map and the interface to apply to
        :param h_pol_int: dictionary of the current configuration of the interface in w_pol_int
        :param delete: flag to specify a delete action
        :param merge: flag to specify a merge action
        :param replace: flag to specify a replace action
        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        cmd = []
        int_name = h_pol_int.get('int_name')
        w_name = w_pol_int.get('policy_name')
        h_name = h_pol_int.get('policy_name')

        # merge
        if merge and int_name and w_name:
            if self.check_policy_maps(w_name):
                if w_name != h_name and h_name and w_name:
                    cmd.append(f"no service-policy input {h_name}")
                if w_name != h_name and w_name:
                    cmd.append(f"service-policy input {w_name}")

        # replace
        if replace and (h_name or w_name):
            if self.check_policy_maps(w_name) or (h_name and not w_name):
                if w_name != h_name and h_name:
                    cmd.append(f"no service-policy input {h_name}")
                if w_name != h_name and w_name:
                    cmd.append(f"service-policy input {w_name}")

        # delete
        if delete and (h_name or w_name):
            if self.check_policy_maps(w_name):
                if w_name == h_name:
                    cmd.append(f"no service-policy input {h_name}")
        if cmd:
            cmd.insert(0, f"interface {int_name}")
        return cmd

    def check_policy_maps(self, name):
        """ Check that the given policy map is available on the host device
        :param name: the name of the policy map to be checked
        :rtype: A bool
        :returns: True if a policy map of the given name exists on the host device,
                  False otherwise
        """
        result = False
        # check for any unsupported characters in name
        if name and not any([item in name for item in [' ', '\\', '|']]):
            pol_maps = self._connection.get(f"show policy-map {name}")
            result = re.search(r"POLICY-MAP-NAME: (\S+)", pol_maps)
        return True if result else False
