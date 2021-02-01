#
# (c) 2019, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_vlans
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusVlansModule(TestAwplusModule):
    module = awplus_vlans

    def setUp(self):
        super(TestAwplusVlansModule, self).setUp()

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

        self.mock_edit_config = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.providers.providers.CliProvider.edit_config"
        )
        self.edit_config = self.mock_edit_config.start()

        self.mock_execute_show_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.vlans.vlans.VlansFacts.get_run_conf"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestAwplusVlansModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_vlan_config.cfg")

        self.execute_show_command.side_effect = load_from_file

    def test_awplus_vlan_default(self):
        set_module_args(dict(config=[dict(vlan_id=30, name="thirty")]))
        commands = ["vlan database", "vlan 30 name thirty"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vlan_default_idempotent(self):
        set_module_args(dict(config=[dict(vlan_id=1, name="default")]))
        self.execute_module(changed=False, commands=[])

    def test_awplus_vlan_merged(self):
        set_module_args(dict(config=[dict(vlan_id=30, name="thirty")], state="merged"))
        commands = ["vlan database", "vlan 30 name thirty"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vlan_merged_idempotent(self):
        set_module_args(dict(config=[dict(vlan_id=1, name="default")], state="merged"))
        self.execute_module(changed=False, commands=[])

    def test_awplus_vlan_replaced(self):
        set_module_args(
            dict(
                config=[dict(vlan_id=30, name="thirty", state="suspend")],
                state="replaced",
            )
        )
        commands = ["vlan database", "vlan 30 name thirty state disable"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vlan_replaced_idempotent(self):
        set_module_args(
            dict(config=[dict(vlan_id=1, name="default")], state="replaced")
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_vlan_overridden(self):
        set_module_args(
            dict(
                config=[
                    dict(vlan_id=1, name="default",),
                    dict(vlan_id=2, name="vlan2",),
                ],
                state="overridden",
            )
        )
        commands = ["vlan database", "no vlan 100"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vlan_overridden_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(vlan_id=1, name="default",),
                    dict(vlan_id=2, name="vlan2",),
                    dict(vlan_id=100, name="VLAN0100",),
                ],
                state="overridden",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_vlan_deleted(self):
        set_module_args(dict(config=[dict(vlan_id=100,)], state="deleted"))
        commands = ["vlan database", "no vlan 100"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vlan_deleted_all(self):
        set_module_args(dict(state="deleted"))
        commands = ["vlan database", "no vlan 100", "no vlan 2"]
        self.execute_module(changed=True, commands=commands)
