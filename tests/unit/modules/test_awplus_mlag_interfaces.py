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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_mlag_interfaces
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusMlagInterfacesModule(TestAwplusModule):

    module = awplus_mlag_interfaces

    def setUp(self):
        super(TestAwplusMlagInterfacesModule, self).setUp()

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
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.mlag_interfaces"
            ".mlag_interfaces.Mlag_interfacesFacts.get_run_mlag_interfaces"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestAwplusMlagInterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_mlag_interfaces_config.cfg")

        self.execute_show_command.side_effect = load_from_file

    def test_awplus_mlag_merge_new(self):
        set_module_args(dict(config=[dict(name="po4", domain_id=10)], state="merged"))
        commands = [
            "interface po4",
            "mlag 10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_merge_existing(self):
        set_module_args(dict(config=[dict(name="po6", domain_id=12)], state="merged"))
        commands = [
            "interface po6",
            "no mlag 10",
            "mlag 12"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_merge_multiple_new(self):
        set_module_args(dict(
            config=[dict(name="po4", domain_id=10), dict(name="po5", domain_id=10)],
            state="merged")
        )
        commands = [
            "interface po4",
            "mlag 10",
            "interface po5",
            "mlag 10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_new(self):
        set_module_args(dict(config=[dict(name="po4", domain_id=10)], state="overridden"))
        commands = [
            "interface po4",
            "mlag 10",
            "interface po6",
            "no mlag 10",
            "interface po7",
            "no mlag 10",
            "interface po8",
            "no mlag 10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_existing(self):
        set_module_args(dict(config=[dict(name="po6", domain_id=12)], state="overridden"))
        commands = [
            "interface po6",
            "no mlag 10",
            "mlag 12",
            "interface po7",
            "no mlag 10",
            "interface po8",
            "no mlag 10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_multiple_new(self):
        set_module_args(dict(
            config=[dict(name="po4", domain_id=10), dict(name="po5", domain_id=10)],
            state="overridden")
        )
        commands = [
            "interface po4",
            "mlag 10",
            "interface po5",
            "mlag 10",
            "interface po6",
            "no mlag 10",
            "interface po7",
            "no mlag 10",
            "interface po8",
            "no mlag 10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_empty(self):
        set_module_args(dict(config=None, state="overridden"))
        commands = [
            "interface po6",
            "no mlag 10",
            "interface po7",
            "no mlag 10",
            "interface po8",
            "no mlag 10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_delete_existing(self):
        set_module_args(dict(config=[dict(name="po6", domain_id=10)], state="deleted"))
        commands = [
            "interface po6",
            "no mlag 10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_delete_non_existing(self):
        set_module_args(dict(config=[dict(name="po4", domain_id=12)], state="deleted"))
        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_awplus_mlag_delete_mutliple(self):
        set_module_args(dict(config=[dict(name="po6"), dict(name="po7")], state="deleted"))
        commands = [
            "interface po6",
            "no mlag 10",
            "interface po7",
            "no mlag 10"
        ]
        self.execute_module(changed=True, commands=commands)
