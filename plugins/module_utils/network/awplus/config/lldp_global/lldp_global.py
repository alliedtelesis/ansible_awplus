#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_lldp_global class
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
from ansible.module_utils.six import (
    iteritems
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import get_lldp_defaults


class Lldp_global(ConfigBase):
    """
    The awplus_lldp_global class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'lldp_global',
    ]

    def __init__(self, module):
        super(Lldp_global, self).__init__(module)

    def get_lldp_global_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        lldp_global_facts = facts['ansible_network_resources'].get('lldp_global')
        if not lldp_global_facts:
            return {}
        return lldp_global_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_lldp_global_facts = self.get_lldp_global_facts()
        commands.extend(self.set_config(existing_lldp_global_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_lldp_global_facts = self.get_lldp_global_facts()

        result['before'] = existing_lldp_global_facts
        if result['changed']:
            result['after'] = changed_lldp_global_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_lldp_global_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_lldp_global_facts
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
        commands.extend(self._clear_config(want, have))
        commands.extend(self._set_config(want, have))
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
        commands.extend(self._clear_config(dict(), have))
        return commands

    def _set_config(self, want, have):
        # Set LLDP global config
        commands = []

        self.validate_tx(want, have)
        for key, value in iteritems(want):
            if value is not None and have.get(key) != value:
                commands.append(self.get_command(key, value=value))

        return commands

    def _clear_config(self, want, have):
        # clear LLDP global config
        commands = []

        defaults = get_lldp_defaults()
        for key, value in iteritems(have):
            if value != defaults[key] and want.get(key) is None:
                commands.append(self.get_command(key, value=False))

        return commands

    def get_command(self, key, value=''):
        # returns command based on key & value
        if key == 'enabled':
            lldp_command = 'run'
        else:
            lldp_command = key.replace("_", "-")

        command = ''
        if value:
            if key in ('enabled', 'non_strict_med_tlv_order_check'):
                command = f"lldp {lldp_command}"
            else:
                command = f"lldp {lldp_command} {value}"
        else:
            command = f"no lldp {lldp_command}"
        return command

    def is_valid_tx(self, timer, delay):
        # timer/delay calculator
        return timer >= (4 * delay)

    def validate_tx(self, want, have):
        # check if timer or delay is valid
        if want.get('timer'):
            delay = want.get('tx_delay') if want.get('tx_delay') else have.get('tx_delay')
            if not self.is_valid_tx(want.get('timer'), delay):
                self._module.fail_json(msg=f"Tx Timer Interval cannot be less than 4 times the Tx Delay (Tx Delay is {delay})")
        elif want.get('tx_delay'):
            timer = have.get('timer')
            if not self.is_valid_tx(timer, want.get('tx_delay')):
                self._module.fail_json(msg=f"Tx Delay Interval cannot be more than (Tx Time Interval / 4)(Tx Time Interval is: {timer}")
        return True
