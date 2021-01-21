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
from ansible_collections.alliedtelesis.awplus.plugins.modules import (
    awplus_static_lag_interfaces,
)
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusStaticLagInterfacesModule(TestAwplusModule):

    module = awplus_static_lag_interfaces

    def setUp(self):
        super(TestAwplusStaticLagInterfacesModule, self).setUp()

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

        x = "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.static_lag_interfaces.static_lag_interfaces."
        self.mock_execute_show_run_command = patch(
            x + "Static_lag_interfacesFacts.get_run_conf"
        )
        self.execute_show_run_command = self.mock_execute_show_run_command.start()

        self.mock_execute_show_int_command = patch(
            x + "Static_lag_interfacesFacts.get_int_brief"
        )
        self.execute_show_int_command = self.mock_execute_show_int_command.start()

    def tearDown(self):
        super(TestAwplusStaticLagInterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_run_command.stop()
        self.mock_execute_show_int_command.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_static_lag_interfaces_config.cfg")

        self.execute_show_run_command.side_effect = load_from_file
        self.execute_show_int_command.return_value = ["port1.0.1", "port1.0.2", "port1.0.3", "port1.0.4", "port1.0.5", "port1.0.6", "port1.0.7", "port1.0.8",
                                                      "port1.0.9", "port1.0.10", "port1.0.11", "port1.0.12", "port1.0.13", "port1.0.14", "port1.0.15",
                                                      "port1.0.16", "port1.0.17", "port1.0.18", "port1.0.19", "port1.0.20", "port1.0.21", "port1.0.22",
                                                      "port1.0.23", "port1.0.24", "port1.0.25", "port1.0.26", "port1.0.27", "port1.0.28", "port1.0.29",
                                                      "port1.0.30", "port1.0.31", "port1.0.32", "port1.0.33", "port1.0.34", "port1.0.35", "port1.0.36",
                                                      "port1.0.37", "port1.0.38", "port1.0.39", "port1.0.40", "port1.0.41", "port1.0.42", "port1.0.43",
                                                      "port1.0.44", "port1.0.45", "port1.0.46", "port1.0.47", "port1.0.48", "port1.0.49", "port1.0.50",
                                                      "port1.0.51", "port1.0.52", "eth1", "sa2", "sa3", "vlan1", "vlan2"]

    def test_awplus_static_lag_interfaces_default(self):
        set_module_args(
            dict(
                config=[{'name': "2", 'members': ["port1.0.5"], 'member-filters': True}]
            )
        )
        commands = ["interface port1.0.5", "static-channel-group 2 member-filters"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_static_lag_interfaces_default_idempotent(self):
        set_module_args(
            dict(
                config=[{'name': "2", 'members': ["port1.0.2"], 'member-filters': True}]
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_static_lag_interfaces_merged(self):
        set_module_args(
            dict(
                config=[{'name': "4", 'members': ["port1.0.5"], 'member-filters': False}],
                state="merged",
            )
        )
        commands = ["interface port1.0.5", "static-channel-group 4"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_static_lag_interfaces_merged_idempotent(self):
        set_module_args(
            dict(
                config=[{'name': "3", 'members': ["port1.0.4"], 'member-filters': False}],
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_static_lag_interfaces_replaced(self):
        set_module_args(
            dict(
                config=[{'name': "2", 'members': ["port1.0.4"], 'member-filters': True}],
                state="replaced",
            )
        )
        commands = [
            "interface port1.0.2",
            "no static-channel-group",
            "interface port1.0.4",
            "no static-channel-group",
            "static-channel-group 2 member-filters",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_static_lag_interfaces_replaced_idempotent(self):
        set_module_args(
            dict(
                config=[{'name': "2", 'members': ["port1.0.2"], 'member-filters': True}],
                state="replaced",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_static_lag_interfaces_overridden(self):
        set_module_args(
            dict(
                config=[{'name': "3", 'members': ["port1.0.2"], 'member-filters': False}],
                state="overridden",
            )
        )
        commands = [
            "interface port1.0.2",
            "no static-channel-group",
            "static-channel-group 3",
            "interface port1.0.4",
            "no static-channel-group",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_static_lag_interfaces_overridden_idempotent(self):
        set_module_args(
            dict(
                config=[{'name': "2", 'members': ["port1.0.2"], 'member-filters': True},
                        {'name': "3", 'members': ["port1.0.4"], 'member-filters': False}],
                state="overridden",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_static_lag_interfaces_deleted(self):
        set_module_args(dict(config=[{'name': "2", 'member-filters': True}], state="deleted"))
        commands = ["interface port1.0.2", "no static-channel-group"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_static_lag_interfaces_delete_all(self):
        set_module_args(dict(config=[{'name': "2", 'member-filters': True},
                                     {'name': "3", 'member-filters': True}], state="deleted"))
        commands = ["interface port1.0.2",
                    "no static-channel-group",
                    "interface port1.0.4",
                    "no static-channel-group"]
        self.execute_module(changed=True, commands=commands)
