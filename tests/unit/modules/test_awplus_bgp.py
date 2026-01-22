# (c) 2020 Allied Telesis
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_bgp
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusBgpModule(TestAwplusModule):

    module = awplus_bgp

    def setUp(self):
        super(TestAwplusBgpModule, self).setUp()

        self.mock_get_config = patch(
            'ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.get_config'
        )
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch(
            'ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.load_config'
        )
        self.load_config = self.mock_load_config.start()

        self.mock_get_resource_connection_config = patch(
            'ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection'
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            'ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection'
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

        self.mock_edit_config = patch(
            'ansible_collections.alliedtelesis.awplus.plugins.module_utils.providers.providers.CliProvider.edit_config'
        )
        self.edit_config = self.mock_edit_config.start()

        self.mock_execute_show_command = patch(
            'ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.bgp.bgp.BgpFacts.get_device_data'
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestAwplusBgpModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None, transport='cli'):
        def load_from_file(*args, **kwargs):
            return load_fixture('awplus_bgp_config.cfg')

        self.execute_show_command.side_effect = load_from_file

    def test_awplus_bgp_merged(self):
        set_module_args(dict(config=dict(bgp_as=100, router_id='192.0.2.2'), state='merged'))
        commands = ['router bgp 100', 'bgp router-id 192.0.2.2']
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_merged_idempotent(self):
        set_module_args(dict(config=dict(bgp_as=100, router_id='1.2.3.4'), state='merged'))
        self.execute_module(changed=False)

    def test_awplus_bgp_add_neighbor(self):
        set_module_args(dict(config=dict(bgp_as=100, neighbors=[dict(
            neighbor='1.2.2.2', remote_as=3)]), state='merged'))
        commands = ['router bgp 100', 'neighbor 1.2.2.2 remote-as 3']
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_add_network(self):
        set_module_args(dict(config=dict(bgp_as=100, networks=[dict(
            prefix='4.2.2.2', route_map='map1')]), state='merged'))
        commands = ['router bgp 100', 'network 4.2.2.2/32 route-map map1']
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_conf_existing_neighbor(self):
        set_module_args(dict(config=dict(bgp_as=100, neighbors=[dict(
            neighbor='1.1.1.1', remote_as=3, enabled=False)]), state='merged'))
        commands = ['router bgp 100', 'neighbor 1.1.1.1 shutdown']
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_add_neighbor_to_af(self):
        set_module_args(dict(config=dict(bgp_as=100, ipv4_address_family=[dict(vrf='red', neighbors=[
            dict(neighbor='2.3.3.3', remote_as=4, remove_private_as=True)])]), state='merged'))
        commands = ['router bgp 100', 'address-family ipv4 vrf red',
                    'neighbor 2.3.3.3 remote-as 4', 'neighbor 2.3.3.3 remove-private-as',
                    'exit-address-family']
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_deleted(self):
        set_module_args(dict(config=dict(bgp_as=100, router_id='1.2.3.4'), state='deleted'))
        self.execute_module(changed=True, commands=['no router bgp 100'])

    def test_awplus_bgp_replaced(self):
        set_module_args(dict(config=dict(bgp_as=100, router_id='192.0.2.2'), state='replaced'))
        commands = ['no router bgp 100', 'router bgp 100', 'bgp router-id 192.0.2.2']
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_replaced_idempotent(self):
        set_module_args(dict(
            config=dict(bgp_as=100, router_id='1.2.3.4',
                        neighbors=[dict(neighbor='1.1.1.1', remote_as=3)],
                        ipv4_address_family=[dict(vrf='red',
                                             networks=[dict(prefix='2.2.2.2', masklen=32, route_map='f')],
                                             neighbors=[dict(neighbor='6.6.6.6', remote_as=3)])]),
            state='merged'))
        self.execute_module(changed=False)

    def test_awplus_bgp_l2vpn_merge_new(self):
        set_module_args(dict(
            config=dict(bgp_as=100,
                        ebgp_requires_policy=False,
                        network_import_check=False,
                        neighbors=[dict(neighbor="1.1.1.3", remote_as=65001)],
                        l2vpn_address_family=dict(
                            vrfs=[dict(vrf='blue', advertisements=[dict(protocol='ipv4')])],
                            neighbors=[dict(neighbor="1.1.1.3", activate=True)],
                            advertise_all_vni=True
                        )),
            state='merged'))
        commands = [
            'router bgp 100',
            'no bgp ebgp-requires-policy',
            'no bgp network import-check',
            'neighbor 1.1.1.3 remote-as 65001',
            'address-family l2vpn evpn vrf blue',
            'advertise ipv4 unicast',
            'exit-address-family',
            'address-family l2vpn evpn',
            'neighbor 1.1.1.3 activate',
            'exit-address-family'
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_l2vpn_merge_existing_advertisement(self):
        set_module_args(dict(
            config=dict(bgp_as=100,
                        ebgp_requires_policy=False,
                        network_import_check=False,
                        l2vpn_address_family=dict(
                            vrfs=[dict(vrf='red', 
                                       advertisements=[
                                           dict(protocol='ipv6'), 
                                           dict(protocol='ipv4', route_map='test')
                                ])],
                            advertise_all_vni=False
                        )),
            state='merged'))
        commands = [
            'router bgp 100',
            'no bgp ebgp-requires-policy',
            'no bgp network import-check',
            'address-family l2vpn evpn vrf red',
            'advertise ipv6 unicast',
            'advertise ipv4 unicast route-map test',
            'exit-address-family',
            'address-family l2vpn evpn',
            'no advertise-all-vni',
            'exit-address-family'
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_l2vpn_replace_new(self):
        set_module_args(dict(
            config=dict(bgp_as=100,
                        ebgp_requires_policy=False,
                        network_import_check=False,
                        neighbors=[dict(neighbor="1.1.1.3", remote_as=65001)],
                        l2vpn_address_family=dict(
                            vrfs=[dict(vrf='blue', advertisements=[dict(protocol='ipv4')])],
                            neighbors=[dict(neighbor="1.1.1.3", activate=True)],
                            advertise_all_vni=True
                        )),
            state='replaced'))
        commands = [
            'no router bgp 100',
            'router bgp 100',
            'no bgp ebgp-requires-policy',
            'no bgp network import-check',
            'neighbor 1.1.1.3 remote-as 65001',
            'address-family l2vpn evpn vrf blue',
            'advertise ipv4 unicast',
            'advertise-all-vni',
            'exit-address-family',
            'address-family l2vpn evpn',
            'neighbor 1.1.1.3 activate',
            'exit-address-family'
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_bgp_l2vpn_replace_existing(self):
        set_module_args(dict(
            config=dict(bgp_as=100,
                        ebgp_requires_policy=False,
                        network_import_check=False,
                        l2vpn_address_family=dict(
                            vrfs=[dict(vrf='red', advertisements=[dict(protocol='ipv6')])],
                            advertise_all_vni=False
                        )),
            state='replaced'))
        commands = [
            'no router bgp 100',
            'router bgp 100',
            'no bgp ebgp-requires-policy',
            'no bgp network import-check',
            'address-family l2vpn evpn vrf red',
            'advertise ipv6 unicast',
            'exit-address-family'
        ]
        self.execute_module(changed=True, commands=commands)
