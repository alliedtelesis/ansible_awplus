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
    remove_empties,
)
from ansible.module_utils.six import (
    iteritems
)
from ansible.module_utils.common.network import (
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
            commands = self._state_deleted(want, have)
        elif state == 'merged':
            commands = self._state_merged(want, have)
        elif state == 'replaced':
            commands = self._state_replaced(want, have)
        return commands

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        commands.extend(self._state_deleted(want, have))
        commands.extend(self._state_merged(want, dict()))
        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        commands = _set_state(want, have)

        if not have or commands:
            commands.insert(0, f"router bgp {want['bgp_as']}")
        return commands

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

def _set_state(want, have):
    commands = []
    if want.get('router_id') and want.get('router_id') != have.get('router_id'):
        commands.append(f"bgp router-id {want['router_id']}")

    if want.get('ebgp_requires_policy') is True and have.get('ebgp_requires_policy') is False:
        commands.append("bgp ebgp-requires-policy")
    if want.get('ebgp_requires_policy') is False and have.get('ebgp_requires_policy') is not False:
        commands.append("no bgp ebgp-requires-policy")

    if want.get('network_import_check') is True and have.get('network_import_check') is False:
        commands.append("bgp network import-check")
    if want.get('network_import_check') is False and have.get('network_import_check') is not False:
        commands.append("no bgp network import-check")

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
    if want.get('ipv4_address_family'):
        addrfam_commands = generate_ipv4_addrfam_commands(want['ipv4_address_family'], have.get('ipv4_address_family', []))
        commands.extend(addrfam_commands)
    if want.get('l2vpn_address_family'):
        addrfam_commands = generate_l2vpn_addrfam_commands(want['l2vpn_address_family'], have.get('l2vpn_address_family', {}))
        commands.extend(addrfam_commands)
    
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
                    commands.append(f"neighbor {w_neighbor} shutdown")
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


def generate_ipv4_addrfam_commands(want, have):
    commands = []
    w_af = param_list_to_dict(want, unique_key='vrf')
    if have:
        h_af = param_list_to_dict(have, unique_key='vrf')
    else:
        h_af = dict()

    for vrf, stats in iteritems(w_af):
        vrf_commands = []

        if stats.get('redistribute'):
            vrf_commands.extend(generate_redistribute_commands(stats['redistribute'], h_af.get(vrf, {}).get('redistribute', [])))

        if stats.get('networks'):
            network_commands = generate_network_commands(stats['networks'], h_af.get(vrf, {}).get('networks', []))
            vrf_commands.extend(network_commands)

        if stats.get('neighbors'):
            neighbor_commands = generate_af_neighbor_commands(stats['neighbors'], h_af.get(vrf, {}).get('neighbors'))
            vrf_commands.extend(neighbor_commands)

        if vrf_commands or vrf not in h_af:
            vrf_commands.insert(0, f"address-family ipv4 vrf {vrf}")
            vrf_commands.append('exit-address-family')
        commands.extend(vrf_commands)

    return commands

def generate_l2vpn_addrfam_commands(want, have):
    commands = []
    commands.extend(generate_l2vpn_af_global_commands(want, have))
    commands.extend(generate_l2vpn_af_vrf_commands(want.get('vrfs'), have.get('vrfs')))
    return commands

def generate_l2vpn_af_global_commands(want, have):
    commands = []

    print(want, have)
    neighbor_commands = generate_l2vpn_af_neighbor_commands(want.get('neighbors'), have.get('neighbors'))
    
    if want.get('advertise_all_vni') and not have.get('advertise_all_vni'):
        neighbor_commands.append('advertise-all-vni')
    elif not want.get('advertise_all_vni') and have.get('advertise_all_vni'):
        neighbor_commands.append('no advertise-all-vni')

    if neighbor_commands:
        neighbor_commands.insert(0, f"address-family l2vpn evpn")
        neighbor_commands.append('exit-address-family')
        commands.extend(neighbor_commands)
    
    return commands

def generate_l2vpn_af_vrf_commands(want, have):
    commands = []

    if want:
        for w_vrf in want:
            vrf_commands = []
            protocol_match = False
            route_map_match = False
            vrf_match = None
            if have:
                for h_vrf in have:
                    if w_vrf['vrf'] == h_vrf['vrf']:
                        vrf_match = h_vrf
            
            if vrf_match:
                for w_ad in w_vrf['advertisements']:
                    for h_ad in vrf_match['advertisements']:
                        if w_ad['protocol'] == h_ad['protocol']:
                            protocol_match = True
                            if w_ad.get("route_map") == h_ad.get("route_map"):
                                route_map_match = True
                        if not protocol_match or (protocol_match and not route_map_match):
                            command = f"advertise {w_ad['protocol']} unicast" + \
                                (f" route-map {w_ad.get("route_map")}" if w_ad.get("route_map") else "")
                            vrf_commands.append(command)
            else:
                for w_ad in w_vrf['advertisements']:
                    command = f"advertise {w_ad['protocol']} unicast" + \
                        (f" route-map {w_ad.get("route_map")}" if w_ad.get("route_map") else "")
                    print(command)
                    vrf_commands.append(command)

            if vrf_commands:
                vrf_commands.insert(0, f"address-family l2vpn evpn vrf {w_vrf['vrf']}")
                vrf_commands.append("exit-address-family")
                commands.extend(vrf_commands)

    if have:
        for h_vrf in have:
            vrf_commands = []
            protocol_match = False
            route_map_match = False
            vrf_match = None
            for w_vrf in want:
                if w_vrf['vrf'] == h_vrf['vrf']:
                    vrf_match = w_vrf['vrf']
            
            if vrf_match is None:
                command = f"no address-family l2vpn evpn vrf {w_vrf['vrf']}"
                commands.append(command)
                continue
            else:
                for h_ad in h_vrf['advertisements']:
                    for w_ad in vrf_match:
                        if w_ad['protocol'] == h_ad['protocol']:
                            protocol_match = True
                            if w_ad.get("route_map") == h_ad.get("route_map"):
                                route_map_match = True
                        
                        if not protocol_match or (protocol_match and not route_map_match):
                            command = f"no advertise {w_ad['protocol']} unicast" + \
                                (f" route-map {w_ad.get("route_map")}" if w_ad.get("route_map") else "")
                            vrf_commands.append(command)
                
                if vrf_commands:
                    vrf_commands.insert(0, f"address-family l2vpn evpn vrf {w_vrf['vrf']}")
                    vrf_commands.append("exit-address-family")
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
                    commands.append('neighbor {} {}'.format(w_neighbor, key.replace('_', '-'), value))
                elif not value and value != h_neighbors.get(w_neighbor, {}).get(key, False):
                    commands.append('no neighbor {} {}'.format(w_neighbor, key.replace('_', '-'), value))

    return commands

def generate_l2vpn_af_neighbor_commands(want, have):
    commands = []

    if want:
        w_neighbors = param_list_to_dict(want, unique_key='neighbor')
    else:
        return commands
    if have:
        h_neighbors = param_list_to_dict(have, unique_key='neighbor')
    else:
        h_neighbors = dict()

    for w_neighbor, w_args in iteritems(w_neighbors):
        if w_neighbor not in h_neighbors and w_args.get('activate') is True:
            commands.append(f"neighbor {w_neighbor} activate")
    return commands
