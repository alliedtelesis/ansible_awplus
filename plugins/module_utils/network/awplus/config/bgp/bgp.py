#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_bgp class
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
    iteritems,
    remove_empties,
    is_netmask,
    to_masklen,
    to_subnet,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts


class Bgp(ConfigBase):
    """
    The awplus_bgp class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'bgp',
    ]

    def __init__(self, module):
        super(Bgp, self).__init__(module)

    def get_bgp_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        bgp_facts = facts['ansible_network_resources'].get('bgp')
        if not bgp_facts:
            return {}
        return bgp_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_bgp_facts = self.get_bgp_facts()
        commands.extend(self.set_config(existing_bgp_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_bgp_facts = self.get_bgp_facts()

        result['before'] = existing_bgp_facts
        if result['changed']:
            result['after'] = changed_bgp_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_bgp_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_bgp_facts
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
        if have != want:
            commands.extend(self._state_deleted(self, want, have))
            commands.extend(self._state_merged(self, want, dict()))
        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []

        if want.get('router_id') and want.get('router_id') != have.get('router_id'):
            commands.append(f"bpg router-id {want['router_id']}")

        if want.get('log_neighbor_changes') is True and not have.get('log_neighbor_changes'):
            commands.append('bgp log-neighbor-changes')
        elif want.get('log_neighbor_changes') is False and have.get('log_neighbor_changes'):
            commands.append('no bgp log-neighbor-changes')

        if want.get('neighbors'):
            neighbor_commands = generate_neighbor_commands(want['neighbors'], have.get('neighbors', []))
            commands.extend(neighbor_commands)
        if want.get('networks'):
            network_commands = generate_network_commands(want['networks'], have.get('networks', []))
            commands.extend(network_commands)
        if want.get('address_family'):
            addrfam_commands = generate_addrfam_commands(want['address_family'], have.get('address_family', []))
            commands.extend(addrfam_commands)

        if not have or commands:
            commands.insert(0, f"router bgp {want['bgp_as']}")
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
            commands.append(f"no router bgp {want['bgp_as']}")
        elif have:
            commands.append(f"no router bgp {have['bgp_as']}")
        return commands


def generate_network_commands(want, have):
    commands = []

    for w_network in want:

        masklen = w_network.get('masklen', 32)
        if is_netmask(masklen):
            masklen = to_masklen(masklen)
        subnet = to_subnet(w_network['prefix'], masklen)
        prefix = subnet.split('/')[0]
        w_network['prefix'] = prefix

        if remove_empties(w_network) not in have:
            command = f"network {subnet}"
            if w_network.get('route_map'):
                command += f" route-map {w_network['route_map']}"
            if w_network.get('backdoor'):
                command += ' backdoor'
            commands.append(command)

    return commands


def generate_neighbor_commands(want, have):
    commands = []

    w_neighbors = param_list_to_dict(want, unique_key='neighbor')
    if have:
        h_neighbors = param_list_to_dict(have, unique_key='neighbor')
    else:
        h_neighbors = dict()

    diff = dict_diff(h_neighbors, w_neighbors)

    for w_neighbor, stats in iteritems(diff):
        if w_neighbor not in h_neighbors:
            commands.append(f"neighbor {w_neighbor} remote-as {stats['remote_as']}")
        for key, value in iteritems(stats):
            if key == 'remote_as' or value is None:
                continue

            if key == 'enabled':
                if value is False and value != h_neighbors.get(w_neighbor).get('enabled', True):
                    commands.append(f"no neighbor {w_neighbor} shutdown")
                if value and value != h_neighbors.get(w_neighbor).get('enabled', True):
                    commands.append(f"no neighbor {w_neighbor} shutdown")
            elif key == 'timers':
                if value.get('connect'):
                    commands.append(f"neighbor {w_neighbor} timers connect {value['connect']}")
                else:
                    if value.get('keepalive') is None or value.get('holdtime') is None:
                        raise ValueError('keepalive and holdtime required together')
                    commands.append(f"neighbor {w_neighbor} timers {value['keepalive']} {value['holdtime']}")

            else:
                f"neighbor {w_neighbor}, {key.replace('_', '-')} {value}"

    return commands


def generate_addrfam_commands(want, have):
    commands = []
    want = param_list_to_dict(want, unique_key='vrf')
    if have:
        have = param_list_to_dict(have, unique_key='vrf')
    else:
        have = dict()

    for vrf, stats in iteritems(want):
        vrf_commands = []

        if stats.get('redistribute'):
            vrf_commands.extend(generate_redistribute_commands(stats['redistribute'], have.get(vrf, {}).get('redistribute', [])))

        if stats.get('networks'):
            network_commands = generate_network_commands(stats['networks'], have.get(vrf, {}).get('networks', []))
            vrf_commands.extend(network_commands)

        if stats.get('neighbors'):
            neighbor_commands = generate_af_neighbor_commands(stats['neighbors'], have.get(vrf, {}).get('neighbors'))
            vrf_commands.extend(neighbor_commands)

        if vrf_commands or vrf not in have:
            vrf_commands.insert(0, f"address-family ipv4 vrf {vrf}")
            vrf_commands.append('exit-address-family')
        commands.extend(vrf_commands)

    return commands


def generate_redistribute_commands(want, have):
    commands = []

    h_protocols = param_list_to_dict(have, unique_key='protocol')

    for redistribute in want:

        w_protocol = redistribute['protocol']
        if w_protocol in h_protocols and h_protocols[w_protocol].get('route_map') and not redistribute.get('route_map'):
            commands.append(f"no redistribute {w_protocol}")

        if remove_empties(redistribute) not in have:
            if redistribute.get('route_map'):
                f"redistribute {redistribute['protocol']} route-map {redistribute['route_map']}"
            else:
                commands.append(f"redistribute {redistribute['protocol']}")

    return commands


def generate_af_neighbor_commands(want, have):
    commands = []

    w_neighbors = param_list_to_dict(want, unique_key='neighbor')
    if have:
        h_neighbors = param_list_to_dict(have, unique_key='neighbor')
    else:
        h_neighbors = dict()

    diff = dict_diff(h_neighbors, w_neighbors)

    for w_neighbor, stats in iteritems(diff):
        if w_neighbor not in h_neighbors:
            commands.append(f"neighbor {w_neighbor} remote-as {stats['remote_as']}")
        for key, value in iteritems(stats):
            if key == 'remote_as' or value is None:
                continue

            if key == 'maximum_prefix':
                commands.append(f"neighbor {w_neighbor} maximum-prefix {value}")
            elif key == 'prefix_list_in':
                commands.append(f"neighbor {w_neighbor} prefix-list {value} in")
            elif key == 'prefix_list_out':
                commands.append(f"neighbor {w_neighbor} prefix-list {value} out")
            else:
                if value and value != h_neighbors.get(w_neighbor, {}).get(key, False):
                    commands.append(f"neighbor {w_neighbor}, {key.replace('_', '-'), value}")
                elif not value and value != h_neighbors.get(w_neighbor, {}).get(key, False):
                    commands.append(f"no neighbor {w_neighbor} {key.replace('_','-'), value}")

    return commands
