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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_acl
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestACLModule(TestAwplusModule):

    module = awplus_acl

    def setUp(self):
        super(TestACLModule, self).setUp()

        self.mock_load_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.load_config"
        )
        self.load_config = self.mock_load_config.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

        self.mock_edit_config = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.providers.providers.CliProvider.edit_config"
        )
        self.edit_config = self.mock_edit_config.start()

        self.mock_get_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.get_config"
        )
        self.get_config = self.mock_get_config.start()

        self.mock_execute_show_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.acl.acl.AclFacts.get_acl_conf"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestACLModule, self).tearDown()
        self.mock_load_config.stop()
        self.mock_edit_config.stop()
        # self.mock_get_config.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_get_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_acl_config.cfg")
        self.execute_show_command.side_effect = load_from_file

    def test_awplus_acl_merge_empty_config(self):
        set_module_args(dict(config=None))
        self.execute_module(changed=False)

    def test_awplus_acl_merge_empty_ace(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="77",
                                acl_type="standard",
                                aces=None
                            )
                        ]
                    )
                ],
                state="merged"
            )
        )
        commands = ["access-list 77"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_existing_ace(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="104",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="196.146.88.0 0.0.0.255",
                                        destination_addr="any",
                                        action="permit",
                                        protocols="ip",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list 104", "4 permit ip 196.146.88.0 0.0.0.255 any"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_new_ace(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="test2",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="196.144.88.0/24",
                                        source_port_protocol=[
                                            dict(
                                                ne=3
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                eq=54
                                            )
                                        ],
                                        action="permit",
                                        protocols="tcp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list extended test2", "permit tcp 196.144.88.0/24 ne 3 any eq 54"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_multiple_aces(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="104",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="171.42.45.0 0.0.0.255",
                                        destination_addr="any",
                                        action="deny",
                                        protocols="ip",
                                        ace_ID=4
                                    ),
                                    dict(
                                        source_addr="141.143.42.0 0.0.0.255",
                                        destination_addr="any",
                                        action="permit",
                                        protocols="ip",
                                        ace_ID=8
                                    ),
                                    dict(
                                        source_addr="181.185.85.0 0.0.0.255",
                                        destination_addr="any",
                                        action="permit",
                                        protocols="ip",
                                        ace_ID=12
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = [
            "access-list 104", "4 deny ip 171.42.45.0 0.0.0.255 any",
            "8 permit ip 141.143.42.0 0.0.0.255 any",
            "12 permit ip 181.185.85.0 0.0.0.255 any"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_multiple_acls(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="104",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="any",
                                        destination_addr="any",
                                        action="deny",
                                        protocols="ip",
                                        ace_ID=4
                                    )
                                ]
                            ),
                            dict(
                                name="166",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="199.199.99.0 0.0.0.255",
                                        destination_addr="179.179.79.0 0.0.0.255",
                                        action="permit",
                                        protocols="ip"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = [
            "access-list 104", "4 deny ip any any", "access-list 166",
            "permit ip 199.199.99.0 0.0.0.255 179.179.79.0 0.0.0.255"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_multiple_acls(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="67",
                                acl_type="standard",
                                aces=[
                                    dict(
                                        source_addr="171.42.45.0 0.0.0.255",
                                        action="deny"
                                    )
                                ]
                            ),
                            dict(
                                name="153",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="199.199.99.0 0.0.0.255",
                                        destination_addr="179.179.79.0 0.0.0.255",
                                        action="permit",
                                        protocols="ip"
                                    )
                                ]
                            ),
                            dict(
                                name="2006",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="199.199.99.0 0.0.0.255",
                                        destination_addr="152.152.53.0 0.0.0.255",
                                        action="permit",
                                        protocols="ip"
                                    )
                                ]
                            )
                        ]
                    ),
                    dict(
                        afi="IPv6",
                        acls=[
                            dict(
                                name="ipv6_test",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="2001:db8::/64",
                                        destination_addr="2001:db8::f/60",
                                        action="permit",
                                        protocols="icmp",
                                        ace_ID=4
                                    )
                                ]
                            ),
                            dict(
                                name="ipv6_test2",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="2001:db8::/60",
                                        destination_addr="2001:db8::f/66",
                                        action="deny",
                                        protocols="icmp"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = [
            "access-list 67", "deny 171.42.45.0 0.0.0.255", "access-list 153",
            "permit ip 199.199.99.0 0.0.0.255 179.179.79.0 0.0.0.255",
            "access-list 2006", "permit ip 199.199.99.0 0.0.0.255 152.152.53.0 0.0.0.255",
            "ipv6 access-list extended ipv6_test", "4 permit icmp 2001:db8::/64 2001:db8::f/60",
            "ipv6 access-list extended ipv6_test2", "deny icmp 2001:db8::/60 2001:db8::f/66"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_hardware_acl(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="3001",
                                acl_type="hardware",
                                aces=[
                                    dict(
                                        source_addr="any",
                                        destination_addr="any",
                                        action="deny",
                                        protocols="icmp",
                                        ICMP_type_number="8"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list 3001 deny icmp any any icmp-type 8"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_with_extra_parameters(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="hardware_acl",
                                acl_type="hardware",
                                aces=[
                                    dict(
                                        source_addr="192.192.92.0/24",
                                        source_port_protocol=[
                                            dict(
                                                eq=10
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                lt=3
                                            )
                                        ],
                                        action="permit",
                                        protocols="ip",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list hardware hardware_acl", "4 permit ip 192.192.92.0/24 any"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_with_extra_parameters_1(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="hardware_acl",
                                acl_type="hardware",
                                aces=[
                                    dict(
                                        source_addr="192.192.92.0/24",
                                        source_port_protocol=[
                                            dict(
                                                range=[
                                                    dict(
                                                        start=2,
                                                        end=10
                                                    )
                                                ]
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                range=[
                                                    dict(
                                                        start=30,
                                                        end=35
                                                    )
                                                ]
                                            )
                                        ],
                                        action="permit",
                                        protocols="udp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = [
            "access-list hardware hardware_acl",
            "4 permit udp 192.192.92.0/24 range 2 10 any range 30 35"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_with_extra_parameters_2(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="test",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="192.143.87.0/24",
                                        destination_addr="198.143.87.0/24",
                                        action="deny",
                                        protocols="ip",
                                        ace_ID=4,
                                        ICMP_type_number=8
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = [
            "access-list extended test",
            "4 deny ip 192.143.87.0/24 198.143.87.0/24"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_valid_but_incorrect_tcp_udp_1(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="hardware_acl",
                                acl_type="hardware",
                                aces=[
                                    dict(
                                        source_addr="192.192.92.0/24",
                                        source_port_protocol=[
                                            dict(
                                                eq=10
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                lt=3
                                            )
                                        ],
                                        action="permit",
                                        protocols="udp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 eq 10 any lt 3"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_valid_but_incorrect_tcp_udp_2(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="test",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="192.143.87.0/24",
                                        source_port_protocol=None,
                                        destination_addr="192.142.50.0/24",
                                        action="deny",
                                        protocols="tcp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list extended test", "4 deny tcp 192.143.87.0/24 192.142.50.0/24"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_valid_but_incorrect_tcp_udp_3(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="hardware_acl",
                                acl_type="hardware",
                                aces=[
                                    dict(
                                        source_addr="192.192.92.0/24",
                                        source_port_protocol=[
                                            dict(
                                                range=None
                                            )
                                        ],
                                        destination_addr="any",
                                        action="permit",
                                        protocols="udp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 any"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_valid_but_incorrect_tcp_udp_4(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="hardware_acl",
                                acl_type="hardware",
                                aces=[
                                    dict(
                                        source_addr="192.192.92.0/24",
                                        source_port_protocol=[
                                            dict(
                                                range=[
                                                    dict(
                                                        start=7
                                                    )
                                                ]
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                range=[
                                                    dict(
                                                        start=30
                                                    )
                                                ]
                                            )
                                        ],
                                        action="permit",
                                        protocols="udp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 any"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_valid_but_incorrect_tcp_udp_5(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="hardware_acl",
                                acl_type="hardware",
                                aces=[
                                    dict(
                                        source_addr="192.192.92.0/24",
                                        source_port_protocol=[
                                            dict(
                                                range=[
                                                    dict(
                                                        start=None,
                                                        end=None
                                                    )
                                                ]
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                range=[
                                                    dict(
                                                        start=None,
                                                        end=None
                                                    )
                                                ]
                                            )
                                        ],
                                        action="permit",
                                        protocols="udp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 any"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_merge_valid_but_incorrect_tcp_udp_6(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="test3",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="any",
                                        source_port_protocol=[
                                            dict(
                                                range=[
                                                    dict(
                                                        start=6,
                                                        end=7
                                                    )
                                                ]
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                lt=9
                                            )
                                        ],
                                        action="permit",
                                        protocols="udp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        commands = ["access-list extended test3", "permit udp any any lt 9"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_replace_empty_config(self):
        set_module_args(
            dict(
                config=None,
                state="replaced"
            )
        )
        self.execute_module(changed=False)

    def test_awplus_acl_replace_ace(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="test",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="170.42.45.0/24",
                                        source_port_protocol=[
                                            dict(
                                                lt=9
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                gt=9
                                            )
                                        ],
                                        action="deny",
                                        protocols="tcp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="replaced"
            )
        )
        commands = [
            "access-list extended test", "no deny tcp 192.143.87.0/24 lt 1 192.142.50.0/24 eq 50",
            "no deny icmp 196.143.87.0/24 196.142.50.0/24 icmp-type 8", "deny tcp 170.42.45.0/24 lt 9 any gt 9"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_replace_nothing_with_new_acl(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="2005",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="170.42.45.0/24",
                                        destination_addr="any",
                                        action="deny",
                                        protocols="ip"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="replaced"
            )
        )
        self.execute_module(changed=False)

    def test_awplus_acl_replace_multiple_acls(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="2001",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="192.182.99.0 0.0.0.255",
                                        destination_addr="any",
                                        action="permit",
                                        protocols="ip",
                                        ace_ID=4
                                    )
                                ]
                            ),
                            dict(
                                name="72",
                                acl_type="standard",
                                aces=[
                                    dict(
                                        source_addr="180.152.66.0 0.0.0.255",
                                        action="deny"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="replaced"
            )
        )
        commands = [
            "access-list 2001", "no deny ip 170.42.45.0 0.0.0.255 any",
            "no permit ip 141.143.42.0 0.0.0.255 any", "no permit ip 181.185.85.0 0.0.0.255 any",
            "permit ip 192.182.99.0 0.0.0.255 any", "access-list 72", "deny 180.152.66.0 0.0.0.255"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_replace_acls_different_afis(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="2001",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="192.182.99.0 0.0.0.255",
                                        destination_addr="any",
                                        action="permit",
                                        protocols="ip",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    ),
                    dict(
                        afi="IPv6",
                        acls=[
                            dict(
                                name="ipv6_test",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="2090:db8::/64",
                                        destination_addr="2001:db8::f/64",
                                        action="deny",
                                        protocols="icmp"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="replaced"
            )
        )
        commands = [
            "access-list 2001", "no deny ip 170.42.45.0 0.0.0.255 any", "no permit ip 141.143.42.0 0.0.0.255 any",
            "no permit ip 181.185.85.0 0.0.0.255 any", "permit ip 192.182.99.0 0.0.0.255 any",
            "ipv6 access-list extended ipv6_test", "no deny icmp 2001:db8::/64 2001:db8::f/64",
            "deny icmp 2090:db8::/64 2001:db8::f/64"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_replace_numbered_tcp_acl(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="3000",
                                acl_type="hardware",
                                aces=[
                                    dict(
                                        source_addr="192.192.92.0/24",
                                        source_port_protocol=[
                                            dict(
                                                eq=2
                                            )
                                        ],
                                        destination_addr="any",
                                        destination_port_protocol=[
                                            dict(
                                                lt=5
                                            )
                                        ],
                                        action="permit",
                                        protocols="udp",
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="replaced"
            )
        )
        commands = ["access-list 3000 permit udp 192.192.92.0/24 eq 2 any lt 5"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_replace_existing_acl_with_empty_ace(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="test",
                                acl_type="extended",
                                aces=None
                            )
                        ]
                    )
                ],
                state="replaced"
            )
        )
        commands = [
            "access-list extended test", "no deny tcp 192.143.87.0/24 lt 1 192.142.50.0/24 eq 50",
            "no deny icmp 196.143.87.0/24 196.142.50.0/24 icmp-type 8"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_replace_icmp_ace(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="test",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="172.192.92.0/24",
                                        destination_addr="192.192.92.0/24",
                                        action="permit",
                                        protocols="icmp",
                                        ICMP_type_number=8,
                                        ace_ID=4
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="replaced"
            )
        )
        commands = [
            "access-list extended test", "no deny tcp 192.143.87.0/24 lt 1 192.142.50.0/24 eq 50",
            "no deny icmp 196.143.87.0/24 196.142.50.0/24 icmp-type 8",
            "permit icmp 172.192.92.0/24 192.192.92.0/24 icmp-type 8"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_replace_new_acl_with_empty_ace(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="newacltest",
                                acl_type="extended",
                                aces=None
                            )
                        ]
                    )
                ],
                state="replaced"
            )
        )
        self.execute_module(changed=False)

    def test_awplus_acl_override_with_empty_config(self):
        set_module_args(
            dict(
                config=None,
                state="replaced"
            )
        )
        self.execute_module(changed=False)

    def test_awplus_acl_override_existing_acl(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="2001",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="192.182.99.0 0.0.0.255",
                                        destination_addr="any",
                                        action="permit",
                                        protocols="ip"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="overridden"
            )
        )
        commands = [
            "no access-list 72", "no access-list 104", "no access-list 2001",
            "no access-list extended test", "no ipv6 access-list extended ipv6_test",
            "no access-list 3000", "no access-list hardware hardware_acl", "access-list 2001",
            "permit ip 192.182.99.0 0.0.0.255 any"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_override_with_new_acl(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="2010",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="192.182.99.0 0.0.0.255",
                                        destination_addr="any",
                                        action="deny",
                                        protocols="ip"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="overridden"
            )
        )
        commands = [
            "no access-list 72", "no access-list 104", "no access-list 2001", "no access-list extended test",
            "no ipv6 access-list extended ipv6_test", "no access-list 3000", "no access-list hardware hardware_acl",
            "access-list 2010", "deny ip 192.182.99.0 0.0.0.255 any"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_override_with_empty_config_1(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=None
                    )
                ],
                state="overridden"
            )
        )
        commands = [
            "no access-list 72", "no access-list 104", "no access-list 2001",
            "no access-list extended test", "no ipv6 access-list extended ipv6_test",
            "no access-list 3000", "no access-list hardware hardware_acl"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_override_with_empty_config_2(self):
        set_module_args(
            dict(
                config=None,
                state="overridden"
            )
        )
        commands = [
            "no access-list 72", "no access-list 104", "no access-list 2001",
            "no access-list extended test", "no ipv6 access-list extended ipv6_test",
            "no access-list 3000", "no access-list hardware hardware_acl"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_override_with_empty_config_3(self):
        set_module_args(
            dict(
                state="overridden"
            )
        )
        commands = [
            "no access-list 72", "no access-list 104", "no access-list 2001",
            "no access-list extended test", "no ipv6 access-list extended ipv6_test",
            "no access-list 3000", "no access-list hardware hardware_acl"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_delete_ace_of_existing_acl(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="test",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="192.143.87.0/24",
                                        source_port_protocol=[
                                            dict(
                                                lt=1
                                            )
                                        ],
                                        destination_addr="192.142.50.0/24",
                                        destination_port_protocol=[
                                            dict(
                                                eq=50
                                            )
                                        ],
                                        action="deny",
                                        protocols="tcp"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="deleted"
            )
        )
        commands = ["access-list extended test", "no deny tcp 192.143.87.0/24 lt 1 192.142.50.0/24 eq 50"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_delete_ace_of_nonexisting_acl(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="154",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="181.185.85.0 0.0.0.255",
                                        destination_addr="any",
                                        action="deny",
                                        protocols="ip"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="deleted"
            )
        )
        self.execute_module(changed=False)

    def test_awplus_acl_delete_acl(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="hardware_acl",
                                acl_type="hardware",
                                aces=None
                            )
                        ]
                    )
                ],
                state="deleted"
            )
        )
        commands = ["no access-list hardware hardware_acl"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_delete_acls_different_afis(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="2001",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="141.143.42.0 0.0.0.255",
                                        destination_addr="any",
                                        action="permit",
                                        protocols="ip"
                                    ),
                                    dict(
                                        source_addr="181.185.85.0 0.0.0.255",
                                        destination_addr="any",
                                        action="permit",
                                        protocols="ip"
                                    )
                                ]
                            ),
                            dict(
                                name="test",
                                acl_type="extended",
                                aces=None
                            ),
                            dict(
                                name="72",
                                acl_type="standard",
                                aces=None
                            )
                        ]
                    ),
                    dict(
                        afi="IPv6",
                        acls=[
                            dict(
                                name="ipv6_test",
                                acl_type="extended",
                                aces=[
                                    dict(
                                        source_addr="2001:db8::/64",
                                        destination_addr="2001:db8::f/64",
                                        action="deny",
                                        protocols="icmp"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="deleted"
            )
        )
        commands = [
            "access-list 2001", "no permit ip 141.143.42.0 0.0.0.255 any", "no permit ip 181.185.85.0 0.0.0.255 any",
            "no access-list extended test", "no access-list 72", "ipv6 access-list extended ipv6_test",
            "no deny icmp 2001:db8::/64 2001:db8::f/64"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_delete_empty_acl_provide_ace(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        afi="IPv4",
                        acls=[
                            dict(
                                name="72",
                                acl_type="standard",
                                aces=[
                                    dict(
                                        source_addr="any",
                                        protocols="ip",
                                        action="deny"
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state="deleted"
            )
        )
        self.execute_module(changed=False)
