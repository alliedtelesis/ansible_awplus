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
import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base import (
    ConfigBase,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
    remove_empties,
    validate_ip_v6_address,
    validate_ip_address,
)
from ansible.module_utils.six import (
    iteritems
)

from ansible.module_utils.common.network import is_masklen

from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts

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
            return {}
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
                try:
                    self._connection.edit_config(commands)
                except Exception as e:
                    error_match = re.match(r"% All IP addresses configured on interface (\S+) have been removed", e)
                    if not error_match:
                        self._module.fail_json(e)
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

        vrf_changes = 0
        other_changes = 0
        for interface in want:
            if interface['vrf']:
                vrf_change += 1
            if interface['ipv4'] or interface['ipv6']:
                other_changes += 1


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
        if state in ('merged', 'replaced', 'deleted') and not want:
            self._module.fail_json(msg=f"value of config parameter must not be empty for state {state}")

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
        add = self._generate_add('replaced', want, have)
        for interface in add.keys():
            interface_commands = []
            for h_interface in have:
                if h_interface['name'] == interface and h_interface.get('vrf') and add[interface].get('vrf'):
                    interface_commands.append(f"no ip vrf forwarding {h_interface.get('vrf')}")
            interface_commands.extend(self._set_config(add[interface]))
            if interface_commands:
                interface_commands.insert(0, f"interface {interface}")
                commands.extend(interface_commands)
        return commands

    # @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        remove = self._generate_override_remove(want, have)
        # set ipv4 for have to empty if we remove the VRF for an interface
        # to match the actual configuration
        for interface in remove.keys():
            if remove[interface].get('vrf'):
                for i, h_interface in enumerate(have):
                    if interface == h_interface['name']:
                        have[i]['ipv4'] = []
        add = self._generate_add('merged', want, have)
        self._module.warn(str(add, remove))
        interfaces = add.keys() | remove.keys()
        for interface in interfaces:
            interface_commands = []
            if remove.get(interface):
                interface_commands.extend(self._clear_config(remove[interface]))
            if add.get(interface):
                interface_commands.extend(self._set_config(add[interface]))
            if interface_commands:
                interface_commands.insert(0, f"interface {interface}")
                commands.extend(interface_commands)
        return commands

    # @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        add = self._generate_add('merged', want, have)
        for interface in add.keys():
            interface_commands = []
            for h_interface in have:
                if h_interface['name'] == interface and h_interface.get('vrf') and add[interface].get('vrf'):
                    interface_commands.append(f"no ip vrf forwarding {h_interface.get('vrf')}")
            interface_commands.extend(self._set_config(add[interface]))
            if interface_commands:
                interface_commands.insert(0, f"interface {interface}")
                commands.extend(interface_commands)
        return commands

    # @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        remove = self._generate_remove(want, have)
        for interface in remove.keys():
            interface_commands = []
            interface_commands.extend(self._clear_config(remove[interface]))
            if interface_commands:
                interface_commands.insert(0, f"interface {interface}")
                commands.extend(interface_commands)
        return commands

    def _generate_remove(self, want, have, ignore=[]):
        full_remove = {}
        for h_interface in have:
            for w_interface in want:
                if w_interface['name'] == h_interface['name']:
                    remove = {}
                    if 'vrf' not in ignore and h_interface.get('vrf') and \
                            (w_interface.get('vrf') == h_interface.get('vrf')):
                        remove['vrf'] = h_interface.get('vrf')

                    if 'ipv4' not in ignore:
                        w_ipv4s = w_interface.get('ipv4') if w_interface.get('ipv4') else []
                        for w_ip4 in w_ipv4s:
                            matching_address = False
                            h_ipv4s = h_interface.get('ipv4') if h_interface.get('ipv4') else []
                            for h_ip4 in h_ipv4s:
                                if w_ip4['address'] == h_ip4['address']:
                                    matching_address = True
                            if matching_address:
                                r_ip4 = {'address': w_ip4['address']}
                                if remove.get('ipv4'):
                                    remove['ipv4'] += r_ip4
                                else:
                                    remove['ipv4'] = [r_ip4]

                    if 'ipv6' not in ignore:
                        w_ipv6s = w_interface.get('ipv6') if w_interface.get('ipv6') else []
                        for w_ip6 in w_ipv6s:
                            matching_address = False
                            h_ipv6s = h_interface.get('ipv6') if h_interface.get('ipv6') else []
                            for h_ip6 in h_ipv6s:
                                if w_ip6['address'] == h_ip6['address']:
                                    matching_address = True
                            if matching_address:
                                r_ip6 = {'address': w_ip6['address']}
                                if remove.get('ipv6'):
                                    remove['ipv6'] += r_ip6
                                else:
                                    remove['ipv6'] = [r_ip6]

                    full_remove[w_interface['name']] = remove
        return full_remove

    def _generate_add(self, state, want, have):
        full_add = {}
        for w_interface in want:
            matching_interface = False
            for h_interface in have:
                if w_interface['name'] == h_interface['name']:
                    matching_interface = True
                    add = {}
                    if w_interface.get('vrf') and (w_interface.get('vrf') != h_interface.get('vrf')):
                        add['vrf'] = w_interface.get('vrf')
                        # set have ipv4 to empty because adding/removing VRFs removes all addresses
                        h_interface['ipv4'] = []

                    w_ipv4s = w_interface.get('ipv4') if w_interface.get('ipv4') else []
                    for w_ip4 in w_ipv4s:
                        if w_ip4['address'] != 'dhcp':
                            w_ipv4_addr = w_ip4['address'].split('/')
                            if len(w_ipv4_addr) != 2:  # validate ip address
                                self._module.fail_json(msg='Invalid format')
                            if not validate_ip_address(w_ipv4_addr[0]) or not is_masklen(w_ipv4_addr[1]):
                                self._module.fail_json(msg='Invalid IP address')

                        if w_ip4['address'] != 'dhcp' and (w_ip4.get('dhcp_client') or w_ip4.get('dhcp_hostname')):
                            self._module.fail_json("Cannot set dhcp args for a static address.")
                        if w_ip4['address'] == 'dhcp' and w_ip4.get('secondary'):
                            self._module.fail_json("Cannot set a secondary address when using DHCP.")

                        matching_address = False
                        dhcp_client = None
                        dhcp_hostname = None
                        secondary = None
                        h_ipv4s = h_interface.get('ipv4') if h_interface.get('ipv4') else []
                        for h_ip4 in h_ipv4s:
                            if w_ip4['address'] == h_ip4['address']:
                                matching_address = True
                                if state == 'merged':
                                    if w_ip4.get('dhcp_client') != h_ip4.get('dhcp_client'):
                                        dhcp_client = w_ip4['dhcp_client']
                                    if w_ip4.get('dhcp_hostname') != h_ip4.get('dhcp_hostname'):
                                        dhcp_hostname = w_ip4['dhcp_hostname']
                                    if w_ip4.get('secondary') != h_ip4.get('secondary'):
                                        secondary = w_ip4['secondary']
                                elif state == 'replaced':
                                    dhcp_client = w_ip4.get('dhcp_client')
                                    dhcp_hostname = w_ip4.get('dhcp_hostname')
                                    secondary = w_ip4.get('secondary')
                        if not matching_address:
                            dhcp_client = w_ip4.get('dhcp_client')
                            dhcp_hostname = w_ip4.get('dhcp_hostname')
                            secondary = w_ip4.get('secondary')

                        if not matching_address or (matching_address and (dhcp_client or dhcp_hostname or secondary)):
                            a_ip4 = {
                                'address': w_ip4['address'],
                                'dhcp_client': dhcp_client,
                                'dhcp_hostname': dhcp_hostname,
                                'secondary': secondary
                            }
                            if add.get('ipv4'):
                                add['ipv4'] += a_ip4
                            else:
                                add['ipv4'] = [a_ip4]

                    w_ipv6s = w_interface.get('ipv6') if w_interface.get('ipv6') else []
                    for w_ip6 in w_ipv6s:
                        matching_address = False
                        h_ipv6s = h_interface.get('ipv6') if h_interface.get('ipv6') else []
                        for h_ip6 in h_ipv6s:
                            w_ipv6_addr = w_ip6['address'].split('/')
                            if len(w_ipv6_addr) != 2:  # validate ipv6 address
                                self._module.fail_json(msg='Invalid format')
                            if not validate_ip_v6_address(w_ipv6_addr[0]) or int(w_ipv6_addr[1]) > 64:
                                self._module.fail_json(msg='Invalid IP address')

                            if w_ip6['address'] == h_ip6['address']:
                                matching_address = True

                        self._module.warn(str(matching_address))
                        if not matching_address:
                            a_ip6 = {'address': w_ip6['address']}
                            if add.get('ipv6'):
                                add['ipv6'] += a_ip6
                            else:
                                add['ipv6'] = [a_ip6]
                    full_add[w_interface['name']] = add
            if not matching_interface:
                full_add[w_interface['name']] = w_interface

        return full_add

    def _generate_override_remove(self, want, have):
        full_remove = {}
        for h_interface in have:
            matching_interface = False
            remove = {}
            for w_interface in want:
                if w_interface['name'] == h_interface['name']:
                    matching_interface = True
                    if h_interface.get('vrf') and (w_interface.get('vrf') != h_interface.get('vrf')):
                        remove['vrf'] = h_interface.get('vrf')

                    matching_address = False
                    dhcp_client = None
                    dhcp_hostname = None
                    secondary = None
                    h_ipv4s = h_interface.get('ipv4') if h_interface.get('ipv4') else []
                    for h_ip4 in h_ipv4s:
                        w_ipv4s = w_interface.get('ipv4') if w_interface.get('ipv4') else []
                        for w_ip4 in w_ipv4s:
                            if w_ip4['address'] == h_ip4['address']:
                                matching_address = True
                                if w_ip4.get('dhcp_client') != h_ip4.get('dhcp_client'):
                                    dhcp_client = w_ip4['dhcp_client']
                                if w_ip4.get('dhcp_hostname') != h_ip4.get('dhcp_hostname'):
                                    dhcp_hostname = w_ip4['dhcp_hostname']
                                if w_ip4.get('secondary') != h_ip4.get('secondary'):
                                    secondary = w_ip4['secondary']
                        if ((dhcp_client or dhcp_hostname or secondary) and matching_address) or not matching_address:
                            r_ip4 = {'address': h_ip4['address']}
                            if remove.get('ipv4'):
                                remove['ipv4'] += r_ip4
                            else:
                                remove['ipv4'] = [r_ip4]

                    h_ipv6s = h_interface.get('ipv6') if h_interface.get('ipv6') else []
                    for h_ip6 in h_ipv6s:
                        matching_address = False
                        w_ipv6s = w_interface.get('ipv6') if w_interface.get('ipv6') else []
                        for w_ip6 in w_ipv6s:
                            if w_ip6['address'] == h_ip6['address']:
                                matching_address = True
                        if not matching_address:
                            r_ip6 = {'address': w_ip6['address']}
                            if remove.get('ipv6'):
                                remove['ipv6'] += r_ip6
                            else:
                                remove['ipv6'] = [r_ip6]

                    full_remove[h_interface['name']] = remove
            if not matching_interface:
                full_remove[h_interface['name']] = h_interface
        return full_remove

    def _set_config(self, want):
        """ Generate commands based on config that is wanted. """
        commands = []

        if not want:
            return commands

        if want.get('vrf'):
            commands.append(f"ip vrf forwarding {want.get('vrf')}")

        if want.get('ipv4'):
            for waddr in want.get('ipv4'):
                cmd = f"ip address {waddr['address']}"
                if waddr.get('secondary'):
                    cmd += ' secondary'
                if waddr.get('dhcp_client'):
                    cmd += f" client-id vlan{waddr.get('dhcp_client')}"
                if waddr.get('dhcp_hostname'):
                    cmd += f" hostname {waddr.get('dhcp_hostname')}"
                commands.append(cmd)

        self._module.warn(str(want.get('ipv6')))
        if want.get('ipv6'):
            for waddr in want.get('ipv6'):
                commands.append(f"ipv6 address {waddr['address']}")

        return commands

    def _clear_config(self, want):
        """ Generate commands based on config that is wanted to be cleared. """
        commands = []

        if not want:
            return commands

        if want.get('vrf'):
            commands.append(f"no ip vrf forwarding {want.get('vrf')}")

        if want.get('ipv4'):
            commands.append(f"no ip address")

        if want.get('ipv6'):
            for waddr in want.get('ipv6'):
                commands.append(f"no ipv6 address {waddr.get('address')}")

        return commands
