# (c) 2019, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import (
    awplus_lacp_interfaces,
)
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusLacpInterfacesModule(TestAwplusModule):
    module = awplus_lacp_interfaces

    def setUp(self):
        super(TestAwplusLacpInterfacesModule, self).setUp()

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

        self.mock_execute_show_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts."
            "lacp_interfaces.lacp_interfaces.Lacp_interfacesFacts.get_run_conf"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

        self.mock_execute_show_int_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts."
            "lacp_interfaces.lacp_interfaces.Lacp_interfacesFacts.get_int_brief"
        )
        self.execute_show_int_command = self.mock_execute_show_int_command.start()

    def tearDown(self):
        super(TestAwplusLacpInterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_execute_show_command.stop()
        self.mock_execute_show_int_command.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_lacp_interfaces_config.cfg")

        self.execute_show_command.side_effect = load_from_file
        self.execute_show_int_command.return_value = ["port1.0.1", "port1.0.2", "port1.0.3", "port1.0.4", "eth1", "po1", "po2", "vlan1", "vlan2"]

    def test_awplus_lacp_interfaces_default(self):
        set_module_args(
            dict(config=[dict(name="port1.0.3", port_priority=2, timeout="short")])
        )
        commands = ["interface port1.0.3", "lacp port-priority 2", "lacp timeout short"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_interfaces_default_idempotent(self):
        set_module_args(
            dict(config=[dict(name="port1.0.2", port_priority=3, timeout="long")])
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_lacp_interfaces_merged(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.2", port_priority=4, timeout="short"),
                    dict(name="port1.0.3", port_priority=3),
                ],
                state="merged",
            )
        )
        commands = [
            "interface port1.0.2",
            "lacp port-priority 4",
            "lacp timeout short",
            "interface port1.0.3",
            "lacp port-priority 3",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_interfaces_merged_idempotent(self):
        set_module_args(
            dict(
                config=[dict(name="port1.0.2", port_priority=3, timeout="long")],
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_lacp_interfaces_replaced(self):
        set_module_args(
            dict(
                config=[dict(name="port1.0.2", port_priority=1, timeout="short")],
                state="replaced",
            )
        )
        commands = ["interface port1.0.2", "lacp port-priority 1", "lacp timeout short"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_interfaces_replaced_idempotent(self):
        set_module_args(
            dict(
                config=[dict(name="port1.0.2", port_priority=3, timeout="long")],
                state="replaced",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_lacp_interfaces_overridden(self):
        set_module_args(
            dict(
                config=[dict(name="port1.0.3", port_priority=2, timeout="short")],
                state="overridden",
            )
        )
        commands = [
            "interface port1.0.2",
            "no lacp port-priority",
            "interface port1.0.3",
            "lacp port-priority 2",
            "lacp timeout short",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_interfaces_overridden_idempotent(self):
        set_module_args(
            dict(config=[dict(name="port1.0.2", port_priority=3)], state="overridden")
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_lacp_interfaces_deleted(self):
        set_module_args(dict(config=[dict(name="port1.0.2",)], state="deleted"))
        commands = ["interface port1.0.2", "no lacp port-priority"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_interfaces_deleted_empty(self):
        set_module_args(dict(state="deleted"))
        self.execute_module(changed=False, commands=[])
