#
# (c) 2019, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_interfaces
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusInterfacesModule(TestAwplusModule):
    module = awplus_interfaces

    def setUp(self):
        super(TestAwplusInterfacesModule, self).setUp()

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
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

        self.mock_execute_show_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.interfaces.interfaces.InterfacesFacts.get_run_conf"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

        self.mock_execute_show_int_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.interfaces.interfaces.InterfacesFacts.get_int_brief"
        )
        self.execute_show_int_command = self.mock_execute_show_int_command.start()

    def tearDown(self):
        super(TestAwplusInterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()
        self.mock_execute_show_int_command.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_interfaces_config.cfg")

        self.execute_show_command.side_effect = load_from_file
        self.execute_show_int_command.return_value = ["port1.0.1", "port1.0.2", "port1.0.3", "port1.0.4", "vlan1", "vlan2", "eth1"]

    def test_awplus_interfaces_merged(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.3", description="Merged by Ansible Network")
                ],
                state="merged",
            )
        )
        commands = ["interface port1.0.3", "description Merged by Ansible Network"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_interfaces_merged_idempotent(self):
        set_module_args(
            dict(
                config=[dict(name="vlan1", description="Merged by Ansible Network")],
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_interfaces_replaced(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="vlan1",
                        description="Replaced by Ansible Network",
                        mtu=234,
                    )
                ],
                state="replaced",
            )
        )
        commands = [
            "interface vlan1",
            "no description",
            "description Replaced by Ansible Network",
            "mtu 234",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_interfaces_replaced_idempotent(self):
        set_module_args(
            dict(config=[dict(name="port1.0.3", speed=1000, description="Overridden by Ansible Network")], state="replaced")
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_interfaces_delete(self):
        set_module_args(dict(config=[dict(name="port1.0.3",)], state="deleted"))
        commands = ["interface port1.0.3", "no speed", "no description"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_interfaces_speed_full(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="port1.0.4",
                        description="Replaced by Ansible Network",
                        speed="500",
                        duplex="full",
                    )
                ],
                state="replaced",
            )
        )
        commands = [
            "interface port1.0.4",
            "description Replaced by Ansible Network",
            "speed 500",
            "duplex full",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_interfaces_speed_auto(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="port1.0.4",
                        speed="500",
                        duplex="auto",
                    )
                ],
                state="replaced",
            )
        )
        commands = [
            "interface port1.0.4",
            "speed 500",
            "duplex auto",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_interfaces_speed_half(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="port1.0.4",
                        description="Replaced by Ansible Network",
                        duplex="half",
                    )
                ],
                state="replaced",
            )
        )
        commands = [
            "interface port1.0.4",
            "description Replaced by Ansible Network",
            "duplex half",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_interfaces_overridden(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="port1.0.3",
                        description="Overridden by Ansible Network",
                        duplex="auto",
                    ),
                    dict(name="vlan1", description="Merged by Ansible Network",),
                ],
                state="overridden",
            )
        )
        commands = [
            "interface port1.0.3",
            "duplex auto",
            "no speed",
            "interface port1.0.2",
            "no description",
            "no shutdown",
            "no duplex",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_interfaces_overridden_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.2", description="test interface", duplex="full", enabled=False),
                    dict(
                        name="port1.0.3",
                        description="Overridden by Ansible Network",
                        speed=1000,
                    ),
                    dict(name="vlan1", description="Merged by Ansible Network",),
                ],
                state="overridden",
            )
        )
        self.execute_module(changed=False, commands=[])
