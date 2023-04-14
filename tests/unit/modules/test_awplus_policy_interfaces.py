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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_policy_interfaces
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestPolicyInterfacesModule(TestAwplusModule):

    module = awplus_policy_interfaces

    def setUp(self):
        super(TestPolicyInterfacesModule, self).setUp()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_execute_show_policy_int_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.policy_interfaces."
            "policy_interfaces.Policy_interfacesFacts.get_policy_interfaces_conf"
        )
        self.execute_show_policy_int_command = self.mock_execute_show_policy_int_command.start()

        self.mock_check_pol_map = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.policy_interfaces."
            "policy_interfaces.Policy_interfaces.check_policy_maps"
        )
        self.check_pol_map = self.mock_check_pol_map.start()

    def tearDown(self):
        super(TestPolicyInterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_execute_show_policy_int_command.stop()
        self.mock_check_pol_map.stop()

    def load_fixtures(self, commands=None):
        def load_policy_from_file(*args, **kwargs):
            result = load_fixture("awplus_policy_interfaces.cfg")
            return result

        self.execute_show_policy_int_command.side_effect = load_policy_from_file
        self.check_pol_map.return_value = True

    def test_awplus_policy_interfaces_replace_empty_config(self):
        set_module_args(dict(config=None, state='replaced'))
        self.execute_module(changed=False)

    def test_awplus_policy_interfaces_replace_on_unused_interface(self):
        set_module_args(dict(config=[dict(int_name='port1.2.1', policy_name="test_pol_map")], state='replaced'))
        commands = [
            "interface port1.2.1", "service-policy input test_pol_map"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_replace_on_occupied_interface(self):
        set_module_args(dict(config=[dict(int_name='port1.6.2', policy_name="test_2")], state='replaced'))
        commands = [
            "interface port1.6.2", "no service-policy input test", "service-policy input test_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_replace_idempotency_test(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        int_name='port1.6.1',
                        policy_name="test_pol_map"
                    ),
                    dict(
                        int_name='port1.6.2',
                        policy_name='test'
                    ),
                    dict(
                        int_name='1.6.3',
                        policy_name='test_pol_map_2'
                    )
                ],
                state='replaced'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_policy_interfaces_remove_with_replace(self):
        set_module_args(dict(config=[dict(int_name='port1.6.1')], state='replaced'))
        commands = [
            "interface port1.6.1", "no service-policy input test_pol_map"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_replace_with_only_policy_map(self):
        set_module_args(dict(config=[dict(policy_name='pol_map_2')], state='replaced'))
        self.execute_module(changed=False, failed=True)

    def test_awplus_policy_interfaces_merge_empty_config(self):
        set_module_args(dict(config=None, state='merged'))
        self.execute_module(changed=False)

    def test_awplus_policy_interfaces_merge_on_unused_interface(self):
        set_module_args(dict(config=[dict(int_name='port1.6.4', policy_name='test_2')], state='merged'))
        commands = [
            "interface port1.6.4", "service-policy input test_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_merge_on_used_interface(self):
        set_module_args(dict(config=[dict(int_name='port1.6.1', policy_name='test_2')], state='merged'))
        commands = [
            "interface port1.6.1", "no service-policy input test_pol_map", "service-policy input test_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_merge_no_policy_map(self):
        set_module_args(dict(config=[dict(int_name='port1.6.1')], state='merged'))
        self.execute_module(changed=False)

    def test_awplus_policy_interfaces_merge_only_policy_map(self):
        set_module_args(dict(config=[dict(policy_name='test_pol_map')], state='merged'))
        self.execute_module(changed=False, failed=True)

    def test_awplus_policy_interfaces_delete_empty_config(self):
        set_module_args(dict(config=None, state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_policy_interfaces_delete_policy_interface(self):
        set_module_args(dict(config=[dict(int_name='port1.6.1', policy_name='test_pol_map')], state='deleted'))
        commands = [
            "interface port1.6.1", "no service-policy input test_pol_map"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_delete_multiple_policy_interface(self):
        set_module_args(dict(config=[dict(int_name='port1.6.1', policy_name='test_pol_map'), dict(int_name='port1.6.2', policy_name='test')], state='deleted'))
        commands = [
            "interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_override_with_empty_config(self):
        set_module_args(dict(config=None, state='overridden'))
        commands = [
            "interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_override_with_new_policy_interface(self):
        set_module_args(dict(config=[dict(int_name='port1.6.9', policy_name='test')], state='overridden'))
        commands = [
            "interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2",
            "interface port1.6.9", "service-policy input test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_interfaces_override_idempotency_test(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        int_name='port1.6.1',
                        policy_name='test_pol_map'
                    ),
                    dict(
                        int_name='port1.6.2',
                        policy_name='test'
                    ),
                    dict(
                        int_name='port1.6.3',
                        policy_name='test_pol_map_2'
                    )
                ],
                state='overridden'
            )
        )
        self.execute_module(changed=False)
