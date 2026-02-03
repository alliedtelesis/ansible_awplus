#
# (c) 2019, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import (
    awplus_l3_interfaces,
)
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusL3InterfacesModule(TestAwplusModule):
    module = awplus_l3_interfaces

    def setUp(self):
        super(TestAwplusL3InterfacesModule, self).setUp()

        self.mock_get_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.get_config"
        )
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.load_config"
        )
        self.load_config = self.mock_load_config.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"
        )
        self.get_resource_connection_config = (
            self.mock_get_resource_connection_config.start()
        )

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"
        )
        self.get_resource_connection_facts = (
            self.mock_get_resource_connection_facts.start()
        )

        self.mock_execute_show_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.l3_interfaces.l3_interfaces.L3_interfacesFacts.get_device_data"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestAwplusL3InterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_l3_interfaces_config.cfg")

        self.execute_show_command.side_effect = load_from_file

    def test_awplus_l3_interfaces_merged(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan1", ipv4=[dict(address="182.56.3.1/24", secondary=True)]),
                    dict(name="vlan2", ipv6=[dict(address="2001:db8::1/64")]),
                ],
                state="merged",
            )
        )
        commands = [
            "interface vlan1",
            "ip address 182.56.3.1/24 secondary",
            "interface vlan2",
            "ipv6 address 2001:db8::1/64",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_merged_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan1", ipv4=[dict(address="192.168.5.77/24")]),
                    dict(name="vlan2", ipv4=[dict(address="192.168.4.4/24")]),
                ],
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_l3_interfaces_replaced(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="vlan1",
                        ipv4=[dict(address="182.56.3.1/24", secondary="True")],
                    ),
                    dict(
                        name="vlan2",
                        ipv4=[
                            dict(
                                address="dhcp",
                                dhcp_client=3,
                                dhcp_hostname="example.com",
                            )
                        ],
                    ),
                ],
                state="replaced",
            )
        )
        commands = [
            "interface vlan1",
            "ip address 182.56.3.1/24 secondary",
            "interface vlan2",
            "ip address dhcp client-id vlan3 hostname example.com",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_replaced_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="vlan1",
                        ipv4=[dict(address="192.168.5.77/24")],
                    ),
                    dict(name="vlan2", ipv4=[dict(address="192.168.4.4/24")],),
                ],
                state="replaced",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_l3_interfaces_overridden(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan1", ipv4=[dict(address="192.168.5.77/24")]),
                    dict(name="vlan2", ipv4=[dict(address="192.168.4.5/24")]),
                ],
                state="overridden",
            )
        )
        commands = [
            "interface vlan1",
            "no ip vrf forwarding VRF1",
            "ip address 192.168.5.77/24",
            "interface vlan2",
            "no ip address",
            "ip address 192.168.4.5/24",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_override_empty(self):
        set_module_args(
            dict(
                config=[],
                state="overridden",
            )
        )
        commands = [
            "interface vlan1",
            "no ip vrf forwarding VRF1",
            "interface vlan2",
            "no ip address"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_overridden_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan1", ipv4=[dict(address="192.168.5.77/24")], vrf="VRF1"),
                    dict(name="vlan2", ipv4=[dict(address="192.168.4.4/24")]),
                ],
                state="overridden",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_l3_interfaces_deleted(self):
        set_module_args(dict(config=[dict(name="vlan2", ipv4=[dict(address="192.168.4.4/24")])], state="deleted"))
        commands = ["interface vlan2", "no ip address"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_merge_vrf_new(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan2", ipv4=[dict(address="182.56.3.1/24")], vrf="VRF2")
                ],
                state="merged",
            )
        )
        commands = [
            "interface vlan2",
            "ip address 182.56.3.1/24",
            "ip vrf forwarding VRF2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_merge_vrf_existing(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan1", ipv4=[dict(address="182.56.3.1/24")], vrf="VRF2")
                ],
                state="merged",
            )
        )
        commands = [
            "interface vlan1",
            "ip address 182.56.3.1/24",
            "no ip vrf forwarding VRF1",
            "ip vrf forwarding VRF2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_replace_vrf_new(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan2", ipv4=[dict(address="182.56.3.1/24")], vrf="VRF2")
                ],
                state="merged",
            )
        )
        commands = [
            "interface vlan2",
            "ip address 182.56.3.1/24",
            "ip vrf forwarding VRF2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_replace_vrf_existing(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan1", ipv4=[dict(address="182.56.3.1/24")], vrf="VRF2")
                ],
                state="replaced",
            )
        )
        commands = [
            "interface vlan1",
            "ip address 182.56.3.1/24",
            "no ip vrf forwarding VRF1",
            "ip vrf forwarding VRF2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_delete_vrf(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan1", ipv4=[dict(address="182.56.3.1/24")], vrf="VRF1")
                ],
                state="deleted",
            )
        )
        commands = [
            "interface vlan1",
            "no ip vrf forwarding VRF1"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l3_interfaces_override_initial(self):
        set_module_args(
            dict(
                config=[
                    dict(name="vlan1", ipv4=[dict(address="10.37.86.38/27")]),
                    dict(name="vlan2", ipv4=[dict(address="192.168.5.1/24")], ipv6=[dict(address="2001:db8::1/48")], vrf="VRF2"),
                    dict(name="vlan3", ipv4=[dict(address="dhcp")])
                ],
                state="overridden",
            )
        )
        commands = [
            "interface vlan1",
            "ip address 10.37.86.38/27",
            "interface vlan2",
            "no ip vrf forwarding VRF1",
            "ip vrf forwarding VRF2",
            "ip address 192.168.5.1/24",
            "ipv6 address 2001:db8::1/48",
            "interface vlan3",
            "no ip address",
            "ip address dhcp"
        ]
        self.execute_module(changed=True, commands=commands)
