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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_user
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusUserModule(TestAwplusModule):

    module = awplus_user

    def setUp(self):
        super(TestAwplusUserModule, self).setUp()

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
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.user.user.UserFacts.get_run_conf"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestAwplusUserModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_user_config.cfg")

        self.execute_show_command.side_effect = load_from_file

    def test_awplus_user_create(self):
        set_module_args(dict(config=[dict(name="test", configured_password="test")]))
        commands = ["username test privilege 1 password test"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_user_merge_idempotent(self):
        set_module_args(dict(config=[dict(name="ansible", privilege=8)]))
        result = self.execute_module(changed=False)

    def test_awplus_user_replaced(self):
        set_module_args(dict(config=[dict(name="test", configured_password="test")], state="replaced"))
        commands = ["username test privilege 1 password test"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_user_replaced_idempotent(self):
        set_module_args(dict(config=[dict(name="ansible", privilege=8)], state="replaced"))
        result = self.execute_module(changed=False)

    def test_awplus_user_overridden(self):
        set_module_args(dict(config=[dict(name="test", configured_password="test")], state="overridden"))
        commands = ["username test privilege 1 password test",
                    "no username ansible",
                    "no username jin"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_user_overridden_idempotent(self):
        set_module_args(dict(config=[dict(name="ansible", privilege=8), dict(name="jin", privilege=3)], state="overridden"))
        result = self.execute_module(changed=False)

    def test_awplus_user_delete(self):
        set_module_args(dict(config=[dict(name="ansible")], state="deleted"))
        commands = ["no username ansible"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_user_delete_all(self):
        set_module_args(dict(state="deleted"))
        commands = ["no username ansible",
                    "no username jin"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_user_delete_no_user(self):
        set_module_args(dict(config=[dict(name="intern")], state="deleted"))
        result = self.execute_module(changed=False)
