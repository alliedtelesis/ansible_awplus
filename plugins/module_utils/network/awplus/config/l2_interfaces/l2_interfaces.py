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
    dict_diff,
)
from ansible.module_utils.six import (
    iteritems
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts
import re


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

        connection = self._connection
        if state == 'overridden':
            kwargs = {'self': self, 'want': want, 'have': have, 'connection': connection}
            commands = self._state_overridden(**kwargs)
        elif state == 'deleted':
            kwargs = {'self': self, 'want': want, 'have': have, 'connection': connection}
            commands = self._state_deleted(**kwargs)
        elif state == 'merged':
            kwargs = {'self': self, 'want': want, 'have': have, 'connection': connection}
            commands = self._state_merged(**kwargs)
        elif state == 'replaced':
            kwargs = {'self': self, 'want': want, 'have': have, 'connection': connection}
            commands = self._state_replaced(**kwargs)
        return commands

    @staticmethod
    def _state_replaced(self, want, have, connection):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for name, want_dict in iteritems(want):
            if name in have:
                if not check_stackports(connection, name):
                    commands.extend(_do_replace(name, want_dict, have[name], self._module, connection))
        return commands

    @staticmethod
    def _state_overridden(self, want, have, connection):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for name, have_dict in iteritems(have):
            if name in want:
                if not check_stackports(connection, name):
                    commands.extend(_do_replace(name, want[name], have_dict, self._module, connection))
            else:
                want_dict = {'name': name}
                commands.extend(_do_delete(name, want_dict, have_dict, connection))
        return commands

    @staticmethod
    def _state_merged(self, want, have, connection):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []

        for name, want_dict in iteritems(want):
            if name in have:
                if not check_stackports(connection, name):
                    have_dict = have[name]
                    commands.extend(_set_config(name, want_dict, have_dict, self._module, connection))
        return commands

    @staticmethod
    def _state_deleted(self, want, have, connection):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        for name, want_dict in iteritems(want):
            if name in have:
                have_dict = have[name]
                commands.extend(_do_delete(name, want_dict, have_dict, connection))
        return commands


def check_stackports(connection, name):
    """ Checks whether a port is a stackport.

        :param connection: the device connection
        :param name: the name of the interface
        :rtype: bool
        :returns: True if the interface is configured as
                  a stacking port, False otherwise
    """

    port_conf = connection.get(f"show running-config interface {name}")
    return True if re.search(r'stackport', port_conf) else False


def check_vlan_conf(connection, vlans):
    """ Checks whether the incoming vlans are available on the host device

        :param connection: the device connection
        :param vlan: the list of vlans to check
        :rtype: list
        :returns: A list of valid vlans that exist on the device
    """
    valid_vlans = []
    if vlans and None not in vlans:
        for vlan in vlans:
            if '-' in str(vlan):
                split_vlan_range = vlan.split('-')
                vlans_list = list(range(int(split_vlan_range[0]), int(split_vlan_range[1]) + 1))
                vlans_list = [int(item) for item in vlans_list]
            else:
                vlans_list = [int(vlan)]

            for vlan_item in vlans_list:
                result = connection.get(f"show vlan {vlan_item}") if vlan_item is not None and vlan_item != 0 else ''
                if result != '':
                    valid_vlans.append(vlan_item)

    return valid_vlans


def _do_delete(name, want_dict, have_dict, connection):
    """
    Carry out actions for deleting the configuration for a port.
    """
    p_cmd = []
    # Drill down to deletable components
    w_access = want_dict.get('access')
    w_vlan = None if w_access is None else w_access.get('vlan')
    h_access = have_dict.get('access')
    h_vlan = None if h_access is None else h_access.get('vlan')
    w_trunk = want_dict.get('trunk')
    w_native_vlan = None if w_trunk is None else w_trunk.get('native_vlan')
    w_native_vlan_flag = w_native_vlan is not None
    w_allowed_vlans = None if w_trunk is None else w_trunk.get('allowed_vlans')
    h_trunk = have_dict.get('trunk')
    h_native_vlan = None if h_trunk is None else h_trunk.get('native_vlan')
    h_native_vlan_flag = h_native_vlan is not None
    h_allowed_vlans = None if h_trunk is None else h_trunk.get('allowed_vlans')

    # Delete requested components
    if w_vlan and h_vlan:
        if not check_stackports(connection, name):
            if int(w_vlan) == int(h_vlan):
                p_cmd.append('no switchport access vlan')
    if w_native_vlan_flag and h_native_vlan_flag:
        if not check_stackports(connection, name):
            if int(w_native_vlan) == int(h_native_vlan):
                p_cmd.append('no switchport trunk native vlan')
    if w_allowed_vlans and h_allowed_vlans:
        # remove excess spaces in w_allowed_vlans
        w_allowed_vlans = [item.strip() for item in w_allowed_vlans]
        for dv in h_allowed_vlans:
            if dv in w_allowed_vlans:
                if not check_stackports(connection, name):
                    p_cmd.append(f'switchport trunk allowed vlan remove {dv}')
    if not (w_vlan or w_native_vlan_flag or w_allowed_vlans) and (h_access or h_trunk):
        if not check_stackports(connection, name):
            p_cmd.append('switchport mode access')
            p_cmd.append('no switchport access vlan')
    if p_cmd:
        p_cmd.insert(0, f'interface {name}')
    return p_cmd


def _do_replace(name, want_dict, have_dict, module, connection):
    """
    Carry out actions for replacing entire configuration of a port. This is used for
    both replaced and overridden operations.
    """
    p_cmd = []

    # Drill down to deletable components
    w_access = want_dict.get('access')
    w_vlan = None if w_access is None else w_access.get('vlan')
    h_access = have_dict.get('access')
    h_vlan = None if h_access is None else h_access.get('vlan')
    w_trunk = want_dict.get('trunk')
    w_native_vlan = None if w_trunk is None else w_trunk.get('native_vlan')
    w_native_vlan_flag = w_native_vlan is not None
    w_allowed_vlans = [] if w_trunk is None or w_trunk.get('allowed_vlans') is None else w_trunk.get('allowed_vlans')
    h_trunk = have_dict.get('trunk')
    h_native_vlan = None if h_trunk is None else h_trunk.get('native_vlan')
    h_native_vlan_flag = h_native_vlan is not None
    h_allowed_vlans = [] if h_trunk is None or 'allowed_vlans' not in h_trunk else h_trunk.get('allowed_vlans')

    # Carry out replace
    # Check for duplicated wants
    if w_vlan and (w_native_vlan_flag or w_allowed_vlans):
        module.fail_json(msg='Interface should either be trunk or access')
    # Mode change?
    if (h_native_vlan_flag or h_allowed_vlans) and not (w_native_vlan_flag or w_allowed_vlans):
        p_cmd.append('switchport mode access')
    elif (w_native_vlan_flag or w_allowed_vlans) and not (h_native_vlan_flag or h_allowed_vlans):
        p_cmd.append('switchport mode trunk')

    # Set VLAN in access mode
    if w_vlan and (not h_vlan or h_vlan != w_vlan):
        w_vlan = check_vlan_conf(connection, [w_vlan])
        if w_vlan:
            p_cmd.append(f'switchport access vlan {w_vlan[0]}')

    # Set VLAN in trunk mode
    if ((w_native_vlan_flag and (not h_native_vlan_flag or h_native_vlan != w_native_vlan))
            or (w_native_vlan is None and h_native_vlan not in (0, 1, None))):
        if w_native_vlan != 0:
            w_native_vlan = check_vlan_conf(connection, [w_native_vlan])
        else:
            w_native_vlan = [w_native_vlan]
        if w_native_vlan or w_native_vlan == 0:
            p_cmd.append(f'switchport trunk native vlan {"none" if w_native_vlan[0] == 0 else w_native_vlan[0]}')

    # Adjust allowed VLANs
    if (w_allowed_vlans or h_allowed_vlans) and 'switchport mode access' not in p_cmd:
        if h_allowed_vlans:
            h_allowed_vlans = [int(item) for item in h_allowed_vlans]
        # need to check that wanted allowed vlans are configured
        w_allowed_vlans = check_vlan_conf(connection, w_allowed_vlans)

        for rv in w_allowed_vlans:
            if rv not in h_allowed_vlans:
                p_cmd.append(f'switchport trunk allowed vlan add {rv}')
        for rv in h_allowed_vlans:
            if rv not in w_allowed_vlans:
                p_cmd.append(f'switchport trunk allowed vlan remove {rv}')

    if p_cmd:
        p_cmd.insert(0, f'interface {name}')
    return p_cmd


def _set_config(name, want, have, module, connection):
    commands = []

    diff = dict_diff(have, want)
    if diff.get('trunk') and diff.get('access'):
        module.fail_json(msg='Interface should either be trunk or access')

    if diff.get('access'):
        value = diff['access']
        if not have.get('access'):
            commands.append('switchport mode access')
        if value['vlan'] != have.get('access', {}).get('vlan'):
            vlan = check_vlan_conf(connection, [value['vlan']]) if value['vlan'] != 0 else [0]
            if vlan:
                commands.append(f"switchport access vlan {vlan[0]}")

    elif diff.get('trunk'):
        value = diff['trunk']
        if not have.get('trunk'):
            commands.append('switchport mode trunk')
        if value.get('allowed_vlans'):
            # need to check that wanted vlan is configured
            valid_vlan_list = check_vlan_conf(connection, value.get('allowed_vlans'))

            for vlan in valid_vlan_list:
                h_allowed_vlans = have.get('trunk', {}).get('allowed_vlans', [])
                h_allowed_vlans = [int(item) for item in h_allowed_vlans]
                if vlan not in h_allowed_vlans:
                    commands.append(f"switchport trunk allowed vlan add {vlan}")
        if value.get('native_vlan') is not None and value.get('native_vlan') != have.get('trunk', {}).get('native_vlan'):
            native_vlan = check_vlan_conf(connection, [value['native_vlan']]) if value['native_vlan'] != 0 else [0]
            if native_vlan:
                commands.append(f'switchport trunk native vlan {"none" if native_vlan[0] == 0 else native_vlan[0]}')

    if commands:
        commands.insert(0, f"interface {name}")

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
                        commands.append(f"switchport trunk allowed vlan remove {dv}")
        elif have.get('access') and dele.get('access'):
            h_access = have['access']
            d_access = dele['access']
            if h_access.get('vlan') == d_access.get('vlan'):
                commands.append('no switchport access vlan')

    if commands:
        commands.insert(0, f"interface {name}")

    return commands
