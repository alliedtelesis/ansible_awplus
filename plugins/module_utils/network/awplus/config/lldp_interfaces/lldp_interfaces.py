#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_lldp_interfaces class
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
    dict_diff,
)
from ansible.module_utils.six import (
    iteritems
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    remove_duplicate_interface,
)


class Lldp_interfaces(ConfigBase):
    """
    The awplus_lldp_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'lldp_interfaces',
    ]

    def __init__(self, module):
        super(Lldp_interfaces, self).__init__(module)

    def get_lldp_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        lldp_interfaces_facts = facts['ansible_network_resources'].get('lldp_interfaces')
        if not lldp_interfaces_facts:
            return {}
        return lldp_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_lldp_interfaces_facts = self.get_lldp_interfaces_facts()
        commands.extend(self.set_config(existing_lldp_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_lldp_interfaces_facts = self.get_lldp_interfaces_facts()

        result['before'] = existing_lldp_interfaces_facts
        if result['changed']:
            result['after'] = changed_lldp_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_lldp_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_lldp_interfaces_facts
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
        if want:
            want = param_list_to_dict(want)
        have = param_list_to_dict(have)

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
        for key, want_dict in want.items():
            if key in have:
                have_dict = have[key]
                diff = dict_diff(want_dict, have_dict)
                commands.extend(_clear_config(key, want_dict, diff))
                commands.extend(_set_config(key, want_dict, have_dict))

        return remove_duplicate_interface(commands)

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        for key, have_dict in iteritems(have):
            p_have = {key: have_dict}
            if key in want:
                p_want = {key: want[key]}
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
            for key, value in iteritems(have):
                commands.extend(_clear_config(key, dict(), value))

        else:
            for key, value in iteritems(want):
                want_dict = dict(name=key)
                if key in have:
                    have_dict = have[key]
                    diff = dict_diff(want_dict, have_dict)
                    commands.extend(_clear_config(key, want_dict, diff))

        return commands


def _set_config(name, want, have):
    commands = []
    for key, value in iteritems(want):
        if value is None:
            continue

        if key in ('receive', 'transmit'):
            if have.get(key, True) != value:
                prefix = "" if value else "no "
                commands.append(f"{prefix}lldp {key}")

        elif key == 'tlv_select':
            for tlv, stat in iteritems(value):
                if stat is None:
                    continue
                if have.get(key, {}).get(tlv, False) != stat:
                    prefix = "" if stat else "no "
                    commands.append(f"{prefix}lldp tlv-select {tlv.replace('_', '-')}")

        elif key == 'med_tlv_select':
            for tlv, stat in iteritems(value):
                if stat is None:
                    continue
                have_stat = have.get(key, {}).get(tlv, True) if tlv != 'inventory_management' \
                    else have.get(key, {}).get(tlv, False)
                if have_stat != stat:
                    prefix = "" if stat else "no "
                    commands.append(f"{prefix}lldp med-tlv-select {tlv.replace('_', '-')}")

    if commands:
        commands.insert(0, f"interface {name}")

    return commands


def _clear_config(name, want, have):
    commands = []
    for key, value in iteritems(have):
        if value is None:
            continue

        if key in ('receive', 'transmit') and want.get(key) is None:
            commands.append(f"lldp {key}")
        elif key == 'tlv_select':
            for tlv, stat in iteritems(value):
                if stat:
                    commands.append(f"no lldp tlv-select {tlv.replace('_', '-')}")
        elif key == 'med_tlv_select':
            for tlv, stat in iteritems(value):
                if tlv == 'inventory_management':
                    commands.append(f"no lldp med-tlv-select {tlv.replace('_', '-')}")
                else:
                    commands.append(f"lldp med-tlv-select {tlv.replace('_', '-')}")

    if commands:
        commands.insert(0, f"interface {name}")

    return commands
