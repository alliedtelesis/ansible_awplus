#
# (c) 2019, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import (
    awplus_l2_interfaces,
)
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusL2InterfacesModule(TestAwplusModule):
    module = awplus_l2_interfaces

    def setUp(self):
        super(TestAwplusL2InterfacesModule, self).setUp()

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
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.l2_interfaces.l2_interfaces.L2_interfacesFacts.get_run_conf"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

        self.mock_execute_show_int_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.l2_interfaces.l2_interfaces.L2_interfacesFacts.get_int_brief"
        )
        self.execute_show_int_command = self.mock_execute_show_int_command.start()

        self.mock_check_stackports = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.l2_interfaces.l2_interfaces.check_stackports"
        )
        self.check_stackports = self.mock_check_stackports.start()

    def tearDown(self):
        super(TestAwplusL2InterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()
        self.mock_execute_show_int_command.stop()
        self.mock_check_stackports.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_l2_interfaces_config.cfg")

        self.execute_show_command.side_effect = load_from_file
        self.execute_show_int_command.return_value = ["port1.0.1", "port1.0.2", "port1.0.3", "port1.0.4"]
        self.check_stackports.return_value = False

    def test_awplus_l2_interfaces_merged(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.3", trunk=dict(native_vlan=2)),
                    dict(name="port1.0.4", access=dict(vlan=2),),
                ],
                state="merged",
            )
        )
        commands = [
            "interface port1.0.3",
            "switchport mode trunk",
            "switchport trunk native vlan 2",
            "interface port1.0.4",
            "switchport mode access",
            "switchport access vlan 2",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l2_interfaces_merged_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.1", access=dict(vlan=3)),
                    dict(name="port1.0.2", trunk=dict(allowed_vlans=['2']),),
                ],
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_l2_interfaces_replaced(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.3", trunk=dict(native_vlan=2)),
                    dict(name="port1.0.2", access=dict(vlan=4),),
                ],
                state="replaced",
            )
        )
        commands = [
            "interface port1.0.3",
            "switchport mode trunk",
            "switchport trunk native vlan 2",
            "interface port1.0.2",
            "switchport mode access",
            "switchport access vlan 4",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l2_interfaces_replaced_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.1", access=dict(vlan=3)),
                    dict(name="port1.0.2", trunk=dict(allowed_vlans=['2']),),
                ],
                state="replaced",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_l2_interfaces_overridden(self):
        set_module_args(
            dict(
                config=[dict(name="port1.0.1", access=dict(vlan=1))], state="overridden"
            )
        )
        commands = [
            "interface port1.0.1",
            "switchport access vlan 1",
            "interface port1.0.2",
            "switchport mode access",
            "no switchport access vlan",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_l2_interfaces_overridden_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.1", access=dict(vlan=3)),
                    dict(name="port1.0.2", trunk=dict(allowed_vlans=['2']),),
                ],
                state="overridden",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_l2_interfaces_deleted(self):
        set_module_args(dict(config=[dict(name="port1.0.2",)], state="deleted"))
        commands = ["interface port1.0.2", "switchport mode access", "no switchport access vlan"]
        self.execute_module(changed=True, commands=commands)
