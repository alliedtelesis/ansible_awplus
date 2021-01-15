#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_l3_interfaces class
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
    remove_empties,
    validate_ip_v6_address,
    validate_ip_address,
    is_masklen,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    get_have_dict,
    get_interfaces,
    remove_duplicate_interface,
    remove_command_from_config_list,
    add_command_to_config_list,
)
from copy import deepcopy


class L3_interfaces(ConfigBase):
    """
    The awplus_l3_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'l3_interfaces',
    ]

    def __init__(self, module):
        super(L3_interfaces, self).__init__(module)

    def get_l3_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        l3_interfaces_facts = facts['ansible_network_resources'].get('l3_interfaces')
        if not l3_interfaces_facts:
            return []
        return l3_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_l3_interfaces_facts = self.get_l3_interfaces_facts()
        commands.extend(self.set_config(existing_l3_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                warning = self._connection.edit_config(commands).get('response')
                for warn in warning:
                    if warn != '':
                        warnings.append(warn)
            result['changed'] = True
        result['commands'] = commands

        changed_l3_interfaces_facts = self.get_l3_interfaces_facts()

        result['before'] = existing_l3_interfaces_facts
        if result['changed']:
            result['after'] = changed_l3_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_l3_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_l3_interfaces_facts
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
        if state in ('overridden', 'merged', 'replaced') and not want:
            self._module.fail_json(msg='value of config parameter must not be empty for state {0}'.format(state))

        if state == 'overridden':
            commands = self._state_overridden(want, have)
        elif state == 'deleted':
            commands = self._state_deleted(want, have)
        elif state == 'merged':
            commands = self._state_merged(want, have)
        elif state == 'replaced':
            commands = self._state_replaced(want, have)
        return commands

    # @staticmethod
    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for interface in want:
            intfs = get_interfaces(interface['name'])
            for intf in intfs:
                partial_want = deepcopy(interface)
                partial_want['name'] = intf
                have_dict = get_have_dict(intf, have)
                if have_dict is None:
                    self._module.fail_json(msg='Interface does not exist')
                if have_dict:
                    commands.extend(self._clear_config(partial_want, have_dict))
                    commands.extend(self._set_config(partial_want, have_dict))
                else:
                    commands.extend(self._set_config(partial_want, dict()))
        # Remove the duplicate interface call
        return remove_duplicate_interface(commands)

    # @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        for each in have:
            for interface in want:
                if each['name'] in interface['name']:
                    break
            else:
                # We didn't find a matching desired state, which means we can
                # pretend we received an empty desired state.
                interface = dict(name=each['name'])
                kwargs = {'want': interface, 'have': each}
                commands.extend(self._clear_config(**kwargs))
                continue

        # Iterating through want list which now only have range interfaces to be
        # configured
        for interface in want:
            intfs = get_interfaces(interface['name'])
            for intf in intfs:
                partial_want = deepcopy(interface)
                partial_want['name'] = intf
                have_dict = get_have_dict(intf, have)
                if have_dict is None:
                    self._module.fail_json(msg='Interface does not exist')
                if have_dict:
                    commands.extend(self._set_config(partial_want, have_dict))
                else:
                    commands.extend(self._set_config(partial_want, dict()))
        # Remove the duplicate interface call
        return remove_duplicate_interface(commands)

    # @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []

        for interface in want:
            intfs = get_interfaces(interface['name'])
            for intf in intfs:
                partial_want = deepcopy(interface)
                partial_want['name'] = intf
                have_dict = get_have_dict(intf, have)
                if have_dict is None:
                    self._module.fail_json(msg='Interface does not exist')
                if have_dict:
                    commands.extend(self._set_config(partial_want, have_dict))
                else:
                    commands.extend(self._set_config(partial_want, dict()))
            # commands.extend(self._clear_config(dict(), have_dict))

        return commands

    # @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []

        if want:
            for interface in want:
                intfs = get_interfaces(interface['name'])
                for intf in intfs:
                    have_dict = get_have_dict(intf, have)
                    if have_dict is None:
                        self._module.fail_json(msg='Interface does not exist')
                    if have_dict:
                        interface = dict(name=intf)
                        commands.extend(self._clear_config(interface, have_dict))
        else:
            for each in have:
                commands.extend(self._clear_config(dict(), each))

        return remove_duplicate_interface(commands)

    def _set_config(self, want, have):
        # Set the interface config based on the want and have config
        commands = []
        interface = 'interface ' + want['name']

        if want == have:
            return

        if want.get('ipv4'):
            haddr = have.get('ipv4')
            if not haddr:  # if interface has no address, have empty list
                haddr = []
            for waddr in want.get('ipv4'):
                waddr = remove_empties(waddr)
                if waddr not in haddr:  # if wanted address not yet configured, add
                    if waddr.get('address') != 'dhcp':
                        ipv4_addr = waddr['address'].split('/')
                        if len(ipv4_addr) != 2:  # validate ip address
                            self._module.fail_json(msg='Invalid format')
                        if not validate_ip_address(ipv4_addr[0]) or not is_masklen(ipv4_addr[1]):
                            self._module.fail_json(msg='Invalid IP address')
                        cmd = 'ip address {0}'.format(waddr['address'])
                        if waddr.get('secondary'):
                            cmd += ' secondary'
                    elif waddr.get('address') == 'dhcp':
                        cmd = 'ip address dhcp'
                        if waddr.get('dhcp_client'):
                            cmd += ' client-id vlan{0}'.format(waddr.get('dhcp_client'))
                        if waddr.get('dhcp_hostname'):
                            cmd += ' hostname {0}'.format(waddr.get('dhcp_hostname'))
                    add_command_to_config_list(interface, cmd, commands)

        if want.get('ipv6'):
            haddr = have.get('ipv6')
            if not haddr:
                haddr = []
            for waddr in want.get('ipv6'):
                waddr = remove_empties(waddr)
                if waddr not in haddr:
                    ipv6_addr = waddr['address'].split('/')
                    if len(ipv6_addr) != 2:  # validate ipv6 address
                        self._module.fail_json(msg='Invalid format')
                    if not validate_ip_v6_address(ipv6_addr[0]) or int(ipv6_addr[1]) > 64:
                        self._module.fail_json(msg='Invalid IP address')
                    cmd = 'ipv6 address {0}'.format(waddr['address'])
                    add_command_to_config_list(interface, cmd, commands)

        return commands

    def _clear_config(self, want, have):
        # Delete the interface config based on the want and have config
        count = 0
        commands = []
        if want.get('name'):
            interface = 'interface ' + want['name']
        else:
            interface = 'interface ' + have['name']

        if have.get('ipv4') and want.get('ipv4'):
            for each in have.get('ipv4'):
                if each.get('secondary') and not (want.get('ipv4')[count].get('secondary')):
                    cmd = 'ip address {0} secondary'.format(each.get('address'))
                    remove_command_from_config_list(interface, cmd, commands)
                if each.get('dhcp_client') or each.get('dhcp_hostname'):
                    if each.get('dhcp_client') != (want.get('ipv4')[count].get('dhcp_client')):
                        cmd = 'ip address dhcp'
                        remove_command_from_config_list(interface, cmd, commands)
                    elif each.get('dhcp_hostname') != (want.get('ipv4')[count].get('dhcp_hostname')):
                        cmd = 'ip address dhcp'
                        remove_command_from_config_list(interface, cmd, commands)
                count += 1
        if have.get('ipv4') and not want.get('ipv4'):
            remove_command_from_config_list(interface, 'ip address', commands)
        if have.get('ipv6') and not want.get('ipv6'):
            for each in have.get('ipv6'):
                remove_command_from_config_list(interface, 'ipv6 address {0}'.format(each.get('address')), commands)
        return commands
