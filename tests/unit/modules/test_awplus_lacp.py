# (c) 2019, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_lacp
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusLacpInterfacesModule(TestAwplusModule):
    module = awplus_lacp

    def setUp(self):
        super(TestAwplusLacpInterfacesModule, self).setUp()

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

        self.mock_edit_config = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.providers.providers.CliProvider.edit_config"
        )
        self.edit_config = self.mock_edit_config.start()

        self.mock_execute_show_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.lacp.lacp.LacpFacts.get_lacp_config"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

        self.mock_execute_show_run_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.lacp.lacp.LacpFacts.get_running_config"
        )
        self.execute_show_run_command = self.mock_execute_show_run_command.start()

    def tearDown(self):
        super(TestAwplusLacpInterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()
        self.mock_execute_show_run_command.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_lacp_from_file(*args, **kwargs):
            return load_fixture("awplus_lacp_config.cfg")

        def load_running_config_from_file(*args, **kwargs):
            return load_fixture("awplus_config_config.cfg")

        self.execute_show_command.side_effect = load_lacp_from_file
        self.execute_show_run_command.side_effect = load_running_config_from_file

    def test_awplus_lacp_default(self):
        set_module_args(dict(config=dict(system=dict(priority=50))))
        commands = ["lacp system-priority 50"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_default_idempotent(self):
        set_module_args(dict(config=dict(system=dict(priority=9))))
        self.execute_module(changed=False, commands=[])

    def test_awplus_lacp_merged(self):
        set_module_args(dict(config=dict(system=dict(priority=50, global_passive_mode=False)), state="merged"))
        commands = ["lacp system-priority 50", "no lacp global-passive-mode enable"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_only_priority_merged_idempotent(self):
        set_module_args(dict(config=dict(system=dict(priority=50)), state="merged"))
        commands = ["lacp system-priority 50"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_only_gpm_merged_idempotent(self):
        set_module_args(dict(config=dict(system=dict(global_passive_mode=False)), state="merged"))
        commands = ["no lacp global-passive-mode enable"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_merged_idempotent(self):
        set_module_args(dict(config=dict(system=dict(priority=9, global_passive_mode=True)), state="merged"))
        self.execute_module(changed=False, commands=[])

    def test_awplus_lacp_deleted(self):
        set_module_args(dict(config=dict(system=dict(priority=1, global_passive_mode=True)), state="deleted"))
        commands = ["no lacp system-priority", "no lacp global-passive-mode enable"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_only_priority_deleted(self):
        set_module_args(dict(config=dict(system=dict(priority=1)), state="deleted"))
        commands = ["no lacp system-priority"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lacp_only_gpm_deleted(self):
        set_module_args(dict(config=dict(system=dict(global_passive_mode=True)), state="deleted"))
        commands = ["no lacp global-passive-mode enable"]
        self.execute_module(changed=True, commands=commands)
