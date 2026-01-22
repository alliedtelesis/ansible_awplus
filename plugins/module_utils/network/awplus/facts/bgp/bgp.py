#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus bgp fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible.module_utils.six import (
    iteritems
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.bgp.bgp import BgpArgs
from ansible.module_utils.connection import ConnectionError


class BgpFacts(object):
    """ The awplus bgp fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = BgpArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_device_data(self, connection):
        try:
            ret = connection.get('show running-config bgp')
        except ConnectionError:
            ret = ""
        return ret

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for bgp
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            # typically data is populated from the current device configuration
            data = self.get_device_data(connection)

        objs = {}
        resources = data.split('!')
        config = deepcopy(self.generated_spec)
        for resource in resources:
            obj = self.render_config(config, resource)
            if obj:
                objs.update(obj)

        ansible_facts['ansible_network_resources'].pop('bgp', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['bgp'] = utils.remove_empties(params['config'])

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, config, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        if not conf:
            return

        if 'address-family ipv4' in conf:
            parse_addressfamily_ipv4(config, conf)
        elif 'address-family l2vpn evpn' in conf:
            parse_addressfamily_l2vpn(config, conf)
        elif 'router bgp' in conf:
            parse_bgp(config, conf)
        return utils.remove_empties(config)


def parse_bgp(config, conf):
    config['bgp_as'] = utils.parse_conf_arg(conf, 'router bgp')
    config['router_id'] = utils.parse_conf_arg(conf, 'bgp router-id')
    if 'bgp log-neighbor-changes' in conf:
        config['log_neighbor_changes'] = True

    if 'no bgp ebgp-requires-policy' in conf:
        config['ebgp_requires_policy'] = False

    if 'no bgp network import-check' in conf:
        config['network_import_check'] = False

    lines = conf.split('\n')
    config['neighbors'] = get_neighbors(lines)
    config['networks'] = get_networks(conf)


def parse_addressfamily_ipv4(config, conf):
    addr_fam = {}
    addr_fam['vrf'] = utils.parse_conf_arg(conf, 'vrf')
    lines = conf.split('\n')
    addr_fam['redistribute'] = get_redistribute(conf)
    addr_fam['neighbors'] = get_neighbors(lines)
    addr_fam['networks'] = get_networks(conf)

    if config['ipv4_address_family']:
        config['ipv4_address_family'].append(addr_fam)
    else:
        config['ipv4_address_family'] = [addr_fam]

def parse_addressfamily_l2vpn(config, conf):
    if not config['l2vpn_address_family']:
        config['l2vpn_address_family'] = {}

    lines = conf.split('\n')
    match = re.match(r' *address-family l2vpn evpn vrf (\S+)', lines[0])
    if match:
        vrf_name = match.group(1)
        advertisements = parse_addressfamily_l2vpn_vrf(lines)
        vrf = dict(name=vrf_name, advertisements=advertisements)
        if config['l2vpn_address_family'].get('vrfs'):
            config['l2vpn_address_family']['vrfs'].append(vrf)
        else:
            config['l2vpn_address_family']['vrfs'] = [vrf]
    else:
        neighbours = parse_addressfamily_l2vpn_neighbor(lines)
        if neighbours and config['l2vpn_address_family'].get('neighbors'):
            config['l2vpn_address_family']['neighbors'].extend(neighbours)
        elif neighbours:
            config['l2vpn_address_family']['neighbors'] = neighbours

        flags = parse_af_l2vpn_flags(lines)
        for arg, val in iteritems(flags):
            config['l2vpn_address_family'][arg] = val

def parse_addressfamily_l2vpn_vrf(lines):
    advertisements = []
    advertisement = {}
    for line in lines:
        match = re.match(r' *?advertise ?(\S+)? ?(\S+)? ?(\S+)? ?(\S+)?', line)
        if not match:
            continue

        if match.group(1):
            advertisement['protocol'] = match.group(1)
        if match.group(2) != 'unicast':
            advertisement = {}
            continue        
        if match.group(3) != 'route-map':
            advertisements.append(advertisement)
            advertisement = {}
            continue
        if match.group(4):
            advertisement['route_map'] = match.group(4)
            advertisements.append(advertisement)
            advertisement = {}

    return advertisements


def parse_addressfamily_l2vpn_neighbor(lines):
    neighbors = []
    neighbor = {}
    for line in lines:
        match = re.match(r' *?neighbor ?(\S+)? activate', line)
        if not match:
            continue

        if match.group(1):
            neighbor['neighbor'] = match.group(1)
            neighbor['activate'] = True
            neighbors.append(neighbor)
            neighbor = {}    
    return neighbors

def parse_af_l2vpn_flags(lines):
    flags = ['advertise-all-vni']
    flag_dict = {}
    for line in lines:
        for flag in flags:
            if line.strip() == flag:
                flag_dict[flag.replace('-', '_')] = True
    return flag_dict

def get_redistribute(conf):
    redistributes = []

    matches = re.findall(r' *?redistribute (\S+) ?(?:route-map)? ?(\S+)?', conf)
    for match in matches:
        redistribute = {}
        redistribute['protocol'] = match[0]
        if match[1]:
            redistribute['route_map'] = match[1]
        redistributes.append(redistribute)

    return redistributes


def get_neighbors(lines):
    neighbor_params = ['neighbor', 'remote-as', 'update-source', 'password', 'shutdown',
                       'description', 'ebgp-multihop', 'local-as', 'peer-group', 'timers',
                       'remote-as', 'activate', 'remove-private-AS', 'next-hop-self', 'maximum-prefix',
                       'prefix-list']
    neighbors = []
    neighbor = {}
    prev = ''

    for line in lines:
        match = re.match(r' *?(no)? ?neighbor (\S+) (\S+) ?(\S+)? ?(\S+)?', line)

        if not match or match.group(3) not in neighbor_params:
            continue

        if prev != match.group(2):
            prev = match.group(2)
            if neighbor and neighbor.get('remote_as'):
                neighbors.append(neighbor)
            neighbor = {}
        neighbor['neighbor'] = match.group(2)

        if 'timers' in line:
            timers = {}
            if 'connect' in line:
                timers['connect'] = match.group(5)
            else:
                timers['keepalive'] = match.group(4)
                timers['holdtime'] = match.group(5)
            neighbor['timers'] = timers
        elif 'prefix-list' in line:
            if match.group(5) == 'in':
                neighbor['prefix_list_in'] = match.group(4)
            elif match.group(5) == 'out':
                neighbor['prefix_list_out'] = match.group(4)
        else:
            param = match.group(3).replace('-', '_').lower()
            if param == 'shutdown':
                neighbor['enabled'] = False
            elif param in ('activate', 'remove_private_as', 'next_hop_self'):
                neighbor[param] = True if 'no' not in line else False
            else:
                neighbor[param] = match.group(4)
    if neighbor and neighbor.get('remote_as'):
        neighbors.append(neighbor)
    return neighbors


def get_networks(conf):
    nets = re.findall('network (.+)', conf)
    networks = []
    if not nets:
        return networks

    for net in nets:
        network = {}
        if 'route-map' in net:
            match = re.match(r'(\S+) route-map (\S+)', net)
            network['route_map'] = match.group(2)
        else:
            match = re.match(r'([\d./]+)', net)
        prefix, masklen = match.group(1).split('/')
        network['prefix'] = prefix
        network['masklen'] = masklen
        if 'backdoor' in net:
            network['backdoor'] = True
        networks.append(network)

    return networks
