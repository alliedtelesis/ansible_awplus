# (c) 2023 Allied Telesis
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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_static_route
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusStaticRouteModule(TestAwplusModule):

    module = awplus_static_route

    def setUp(self):
        super(TestAwplusStaticRouteModule, self).setUp()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_execute_show_static_route_conf = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.static_route."
            "static_route.Static_routeFacts.get_static_route_conf"
        )
        self.execute_show_static_route_conf = self.mock_execute_show_static_route_conf.start()

        self.mock_check_vrf = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.static_route.static_route.Static_route._check_vrf"
        )
        self.check_vrf = self.mock_check_vrf.start()

    def tearDown(self):
        super(TestAwplusStaticRouteModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_check_vrf.stop()
        self.mock_execute_show_static_route_conf.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_static_route.cfg")

        self.execute_show_static_route_conf.side_effect = load_from_file
        self.check_vrf.return_value = True

    def test_awplus_merge_new_IPv4_static_route_1(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="168.144.2.0/24",
                        next_hop="vlan2",
                        description="a new static route",
                        admin_distance=21,
                        vrf="test"
                    )
                ],
                state="merged"
            )
        )
        commands = [
            "ip route vrf test 168.144.2.0/24 vlan2 21 description a new static route"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_merge_new_IPv4_static_route_2(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="192.168.3.0 255.255.255.0",
                        next_hop="vlan2",
                        admin_distance=21
                    )
                ],
                state="merged"
            )
        )
        commands = [
            "ip route 192.168.3.0/24 vlan2 21"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_merge_new_IPv6_static_route(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv6",
                        address="2100:db8::1/128",
                        next_hop="vlan2",
                        source_address="2010::1",
                        description="a new description",
                        admin_distance=111
                    )
                ],
                state="merged"
            )
        )
        commands = [
            "ipv6 route 2100:db8::1/128 2010::1 vlan2 111 description a new description"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_merge_change_IPv4_static_route_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="191.144.2.0 255.255.255.0",
                        next_hop="vlan1",
                        description="a new description for a route",
                        vrf="test_2"
                    )
                ],
                state="merged"
            )
        )
        commands = [
            "no ip route vrf test 191.144.2.0/24  vlan1",
            "ip route vrf test_2 191.144.2.0/24 vlan1 112 description a new description for a route"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_merge_idempotent_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="191.144.2.0/24",
                        next_hop="vlan1",
                        admin_distance=112,
                        vrf="test"
                    ),
                    dict(
                        afi="IPv6",
                        address="2001:db8::1/128",
                        next_hop="vlan2",
                        source_address="2001::1",
                        description="description"
                    ),
                    dict(
                        afi="IPv4",
                        address="190.144.2.0/24",
                        next_hop="vlan2",
                        admin_distance=12
                    ),
                    dict(
                        afi="IPv4",
                        address="190.144.2.0/24",
                        next_hop="vlan1",
                        admin_distance=121
                    )
                ],
                state="merged"
            )
        )
        self.execute_module(changed=False)

    def test_awplus_replace_nothing_with_new_config(self):
        set_module_args(dict(config=[dict(afi="IPv4", address="168.144.2.0/24", next_hop="vlan2", description="something")], state="replaced"))
        self.execute_module(changed=False)

    def test_awplus_replace_IPv4_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="191.144.2.0/24",
                        next_hop="vlan1",
                        description="a new item",
                        admin_distance=1
                    )
                ],
                state="replaced"
            )
        )
        commands = [
            "no ip route vrf test 191.144.2.0/24  vlan1",
            "ip route 191.144.2.0/24 vlan1 1 description a new item"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_replace_IPv6_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv6",
                        address="2001:db8::1/128",
                        next_hop="vlan2",
                        source_address="2101::1",
                        admin_distance=11
                    )
                ],
                state="replaced"
            )
        )
        commands = [
            "no ipv6 route 2001:db8::1/128 2001::1 vlan2",
            "ipv6 route 2001:db8::1/128 2101::1 vlan2 11"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_replace_idempotent_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="191.144.2.0/24",
                        next_hop="vlan1",
                        admin_distance=112,
                        vrf="test"
                    ),
                    dict(
                        afi="IPv6",
                        address="2001:db8::1/128",
                        next_hop="vlan2",
                        source_address="2001::1",
                        description="description"
                    ),
                    dict(
                        afi="IPv4",
                        address="190.144.2.0/24",
                        next_hop="vlan2",
                        admin_distance=12
                    ),
                    dict(
                        afi="IPv4",
                        address="190.144.2.0/24",
                        next_hop="vlan1",
                        admin_distance=121
                    )
                ],
                state="replaced"
            )
        )
        self.execute_module(changed=False)

    def test_awplus_delete_items_multiple_configs(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv6",
                        address="2001:db8::1/128",
                        next_hop="vlan2",
                        source_address="2001::1"
                    ),
                    dict(
                        afi="IPv4",
                        address="191.144.2.0/24",
                        next_hop="vlan1",
                        vrf="test"
                    )
                ],
                state="deleted"
            )
        )
        commands = [
            "no ip route vrf test 191.144.2.0/24  vlan1",
            "ip route 191.144.2.0/24 vlan1 112",
            "no ipv6 route 2001:db8::1/128 2001::1 vlan2",
            "ipv6 route 2001:db8::1/128 vlan2 description description"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_delete_single_route(self):
        set_module_args(dict(config=[dict(afi="IPv4", address="191.144.2.0/24", next_hop="vlan1")], state="deleted"))
        commands = [
            "no ip route vrf test 191.144.2.0/24 vlan1"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_delete_all_routes_using_same_address(self):
        set_module_args(dict(config=[dict(afi="IPv4", address="190.144.2.0/24")], state="deleted"))
        commands = [
            "no ip route 190.144.2.0/24"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_delete_all_vrf_routes_using_same_address(self):
        set_module_args(dict(config=[dict(afi="IPv4", address="191.144.2.0/24", vrf="test")], state="deleted"))
        self.execute_module(changed=False)

    def test_awplus_overridden_add_new_route_remove_others(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="172.144.2.0 255.255.255.255",
                        admin_distance=21,
                        description="overwritten desp",
                        next_hop="vlan2"
                    )
                ],
                state="overridden"
            )
        )
        commands = [
            "no ip route 190.144.2.0/24 vlan2",
            "no ip route 190.144.2.0/24 vlan1",
            "no ip route vrf test 191.144.2.0/24 vlan1",
            "no ipv6 route 2001:db8::1/128 2001::1 vlan2",
            "ip route 172.144.2.0/32 vlan2 21 description overwritten desp"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_overridden_add_update_remove_configs(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="191.144.2.0 255.255.255.0",
                        next_hop="vlan1",
                        description="a static route",
                        admin_distance=12,
                        vrf="test_2"
                    ),
                    dict(
                        afi="IPv6",
                        address="2001:db8::1/128",
                        next_hop="vlan1",
                        source_address="2001::1",
                        description="description of something"
                    )
                ],
                state="overridden"
            )
        )
        commands = [
            "no ip route 190.144.2.0/24 vlan2",
            "no ip route 190.144.2.0/24 vlan1",
            "no ip route vrf test 191.144.2.0/24  vlan1",
            "ip route vrf test_2 191.144.2.0/24 vlan1 12 description a static route",
            "no ipv6 route 2001:db8::1/128 2001::1 vlan2",
            "ipv6 route 2001:db8::1/128 2001::1 vlan1 description description of something"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_override_idempotent_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        address="191.144.2.0/24",
                        next_hop="vlan1",
                        admin_distance=112,
                        vrf="test"
                    ),
                    dict(
                        afi="IPv6",
                        address="2001:db8::1/128",
                        next_hop="vlan2",
                        source_address="2001::1",
                        description="description"
                    ),
                    dict(
                        afi="IPv4",
                        address="190.144.2.0/24",
                        next_hop="vlan2",
                        admin_distance=12
                    ),
                    dict(
                        afi="IPv4",
                        address="190.144.2.0/24",
                        next_hop="vlan1",
                        admin_distance=121
                    )
                ],
                state="overridden"
            )
        )
        self.execute_module(changed=False)
