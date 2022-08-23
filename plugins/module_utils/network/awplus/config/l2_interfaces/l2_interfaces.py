#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_l2_interfaces class
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


class L2_interfaces(ConfigBase):
    """
    The awplus_l2_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'l2_interfaces',
    ]

    def __init__(self, module):
        super(L2_interfaces, self).__init__(module)

    def get_l2_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        l2_interfaces_facts = facts['ansible_network_resources'].get('l2_interfaces')
        if not l2_interfaces_facts:
            return {}
        return l2_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_l2_interfaces_facts = self.get_l2_interfaces_facts()
        commands.extend(self.set_config(existing_l2_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                warning = self._connection.edit_config(commands).get('response')
                for warn in warning:
                    if warn != '':
                        warnings.append(warn)
            result['changed'] = True
        result['commands'] = commands

        changed_l2_interfaces_facts = self.get_l2_interfaces_facts()

        result['before'] = existing_l2_interfaces_facts
        if result['changed']:
            result['after'] = changed_l2_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_l2_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_l2_interfaces_facts
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

        for name, want_dict in iteritems(want):
            if name in have:
                have_dict = have[name]
                commands.extend(_clear_config(name, want_dict, have_dict))
                commands.extend(_set_config(name, want_dict, have_dict, self._module))

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
                commands.extend(_set_config(name, want_dict, have_dict, self._module))

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
            for name, want_dict in iteritems(want):
                if name in have:
                    have_dict = have[name]
                    commands.extend(_delete_config(name, have_dict, want_dict))
        return commands


def _set_config(name, want, have, module):
    commands = []

    diff = dict_diff(have, want)
    if diff.get('trunk') and diff.get('access'):
        module.fail_json(msg='Interface should either be trunk or access')

    if diff.get('access'):
        value = diff['access']
        if not have.get('access'):
            commands.append('switchport mode access')
        if value['vlan'] != have.get('access', {}).get('vlan'):
            commands.append('switchport access vlan {}'.format(value['vlan']))

    elif diff.get('trunk'):
        value = diff['trunk']
        if not have.get('trunk'):
            commands.append('switchport mode trunk')
        if value.get('allowed_vlans'):
            for vlan in value.get('allowed_vlans'):
                if vlan not in have.get('trunk', {}).get('allowed_vlans', []):
                    commands.append('switchport trunk allowed vlan add {}'.format(vlan))
        if value.get('native_vlan') and value.get('native_vlan') != have.get('trunk', {}).get('native_vlan'):
            commands.append('switchport trunk native vlan {}'.format(value['native_vlan']))

    if commands:
        commands.insert(0, 'interface {}'.format(name))

    return commands


def _clear_config(name, want, have):
    """
    Work out what to clear in order to get from have to want. Apart from having nothing in want, the
    only commands generated apply to trunk mode.
    """
    commands = []

    if not want:
        if have.get('trunk'):
            commands.append('switchport mode access')
        elif have.get('access'):
            commands.append('no switchport access vlan')
    elif have.get('trunk'):
        if not want.get('trunk'):
            commands.append('no switchport trunk')
        else:
            h_trunk = have['trunk']
            w_trunk = want['trunk']
            if h_trunk.get('allowed_vlans'):
                if not w_trunk.get('allowed_vlans'):
                    commands.append('switchport trunk allowed vlan none')
                else:
                    for vid in h_trunk['allowed_vlans']:
                        if vid not in w_trunk['allowed_vlans']:
                            commands.append('switchport trunk allowed vlan remove {}'.format(vid))
            if h_trunk.get('native_vlan') and not w_trunk.get('native_vlan'):
                commands.append('no switchport trunk native vlan')
    if commands:
        commands.insert(0, 'interface {}'.format(name))
    return commands


def _delete_config(name, have, dele):
    commands = []

    if dele:
        if have.get('trunk') and dele.get('trunk'):
            h_trunk = have['trunk']
            d_trunk = dele['trunk']
            if h_trunk.get('native_vlan') == d_trunk.get('native_vlan'):
                commands.append('no switchport trunk native vlan')
            if h_trunk.get('allowed_vlans') and d_trunk.get('allowed_vlans'):
                for dv in d_trunk['allowed_vlans']:
                    if dv in h_trunk['allowed_vlans']:
                        commands.append('switchport trunk allowed vlan remove {}'.format(dv))
        elif have.get('access') and dele.get('access'):
            h_access = have['access']
            d_access = dele['access']
            if h_access.get('vlan') == d_access.get('vlan'):
                commands.append('no switchport access vlan')

    if commands:
        commands.insert(0, 'interface {}'.format(name))

    return commands
