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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_acl_interfaces
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestACLInterfacesModule(TestAwplusModule):

    module = awplus_acl_interfaces

    def setUp(self):
        super(TestACLInterfacesModule, self).setUp()

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

        self.mock_execute_show_running_config = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.acl_interfaces.acl_interfaces.Acl_interfacesFacts."
            "get_running_config"
        )
        self.execute_show_running_config = self.mock_execute_show_running_config.start()

        self.mock_execute_show_port_list = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.acl_interfaces.acl_interfaces.Acl_interfacesFacts.get_port_list"
        )
        self.execute_show_port_list = self.mock_execute_show_port_list.start()

        self.mock_execute_show_access_list = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.acl_interfaces.acl_interfaces.Acl_interfaces.get_acl"
        )
        self.execute_show_access_list = self.mock_execute_show_access_list.start()

    def tearDown(self):
        super(TestACLInterfacesModule, self).tearDown()
        self.mock_load_config.stop()
        self.mock_edit_config.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_get_config.stop()
        self.mock_execute_show_running_config.stop()
        self.mock_execute_show_port_list.stop()
        self.mock_execute_show_access_list.stop()

    def load_fixtures(self, commands=None):
        def load_running_config_from_file(*args, **kwargs):
            return load_fixture("awplus_acl_interfaces_show_interface_config.cfg")

        def load_port_list_from_file(*args, **kwargs):
            return load_fixture("awplus_acl_interfaces_port_list_config.cfg")

        def load_access_list_from_file(*args, **kwargs):
            return load_fixture("awplus_acl_interfaces_access_list_config.cfg")

        self.execute_show_running_config.side_effect = load_running_config_from_file
        self.execute_show_port_list.side_effect = load_port_list_from_file
        self.execute_show_access_list.side_effect = load_access_list_from_file

    def test_awplus_acl_interfaces_merge_empty_config(self):
        set_module_args(dict(config=None))
        self.execute_module(changed=False)

    def test_awplus_acl_interfaces_merge_existing_port_new_acl(self):
        set_module_args(dict(config=[dict(name="port1.6.5", acl_names=["test_acl_4"])]))
        commands = ["interface port1.6.5", "access-group test_acl_4"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_merge_new_port_new_acl(self):
        set_module_args(dict(config=[dict(name="port1.6.6", acl_names=["test_acl_4"])]))
        commands = ["interface port1.6.6", "access-group test_acl_4"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_replace_empty_config(self):
        set_module_args(dict(config=None, state="replaced"))
        self.execute_module(changed=False)

    def test_awplus_acl_interfaces_replace_acl_on_port(self):
        set_module_args(dict(config=[dict(name="port1.6.5", acl_names=["test_acl_4"])], state="replaced"))
        commands = [
            "interface port1.6.5", "no access-group test_acl_3",
            "interface port1.6.5", "access-group test_acl_4"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_replace_new_port_with_acl(self):
        set_module_args(dict(config=[dict(name="port1.6.6", acl_names=["test_acl_4"])], state="replaced"))
        self.execute_module(changed=False)

    def test_awplus_acl_interfaces_replace_port_with_nothing(self):
        set_module_args(dict(config=[dict(name="port1.1.10", acl_names=None)], state="replaced"))
        commands = [
            "interface port1.1.10", "no access-group test_acl_2",
            "no access-group test_acl_1"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_override_with_empty_config_1(self):
        set_module_args(dict(config=None, state="overridden"))
        commands = [
            "interface port1.6.5", "no access-group test_acl_3", "interface port1.1.10",
            "no access-group test_acl_1", "no access-group test_acl_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_override_with_empty_config_2(self):
        set_module_args(dict(config=[dict(name=None)], state="overridden"))
        commands = [
            "interface port1.6.5", "no access-group test_acl_3", "interface port1.1.10",
            "no access-group test_acl_1", "no access-group test_acl_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_override_with_empty_config_3(self):
        set_module_args(dict(config=[dict(name=None)], state="overridden"))
        commands = [
            "interface port1.6.5", "no access-group test_acl_3", "interface port1.1.10",
            "no access-group test_acl_1", "no access-group test_acl_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_override_port_with_empty_acl_list(self):
        set_module_args(dict(config=[dict(name="port1.1.10")], state="overridden"))
        commands = [
            "interface port1.6.5", "no access-group test_acl_3", "interface port1.1.10",
            "no access-group test_acl_1", "no access-group test_acl_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_delete_empty(self):
        set_module_args(dict(config=None))
        self.execute_module(changed=False)

    def test_awplus_acl_interfaces_delete_all_acls_attached_to_port(self):
        set_module_args(dict(config=[dict(name="port1.1.10")], state="deleted"))
        commands = [
            "interface port1.1.10", "no access-group test_acl_1",
            "no access-group test_acl_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_delete_one_acl_attached_port(self):
        set_module_args(dict(config=[dict(name="port1.1.10", acl_names=["test_acl_1"])], state="deleted"))
        commands = [
            "interface port1.1.10", "no access-group test_acl_1"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_acl_interfaces_delete_one_acl_from_different_interfaces(self):
        set_module_args(dict(config=[dict(name="port1.1.10", acl_names=["test_acl_1"]), dict(name="port1.6.5", acl_names=["test_acl_3"])], state="deleted"))
        commands = [
            "interface port1.1.10", "no access-group test_acl_1",
            "interface port1.6.5", "no access-group test_acl_3"
        ]
        self.execute_module(changed=True, commands=commands)
