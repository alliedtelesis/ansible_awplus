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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_premark_dscps
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestPremarkDscpsModule(TestAwplusModule):

    module = awplus_premark_dscps

    def setUp(self):
        super(TestPremarkDscpsModule, self).setUp()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_execute_show_premark_dscps_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts."
            "premark_dscps.premark_dscps.Premark_dscpsFacts.get_premark_dscps_conf"
        )
        self.execute_show_premark_dscps_command = self.mock_execute_show_premark_dscps_command.start()

    def tearDown(self):
        super(TestPremarkDscpsModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_execute_show_premark_dscps_command.stop()

    def load_fixtures(self, commands=None):
        def load_premark_dscps_from_file(*args, **kwargs):
            result = load_fixture("awplus_premark_dscps_get_premark_conf.cfg")
            return result

        self.execute_show_premark_dscps_command.side_effect = load_premark_dscps_from_file

    def test_awplus_premark_dscps_replace_empty_config_1(self):
        set_module_args(dict(config=None, state='replaced'))
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_replace_empty_config_2(self):
        set_module_args(dict(config=[dict(dscp_in=None)], state='replaced'))
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_replace_1_parameter_in_empty_premark_dscps_map(self):
        set_module_args(dict(config=[dict(dscp_in=60, dscp_new=63)], state='replaced'))
        commands = [
            "mls qos map premark-dscp 60 to new-dscp 63"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_replace_all_parameters_in_empty_premark_dscps_map(self):
        set_module_args(dict(config=[dict(dscp_in=60, dscp_new=63, cos_new=3, class_new='red')], state='replaced'))
        commands = [
            "mls qos map premark-dscp 60 to new-dscp 63 new-cos 3 new-bandwidth-class red"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_replace_parameters_in_premark_dscps_map(self):
        set_module_args(dict(config=[dict(dscp_in=63, cos_new=7, class_new='yellow')], state='replaced'))
        commands = [
            "mls qos map premark-dscp 63 to new-dscp 63 new-cos 7 new-bandwidth-class yellow"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_replace_idempotency_test(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        dscp_in=63,
                        dscp_new=40,
                        cos_new=4,
                        class_new='red'
                    ),
                    dict(
                        dscp_in=34,
                        cos_new=4
                    ),
                    dict(
                        dscp_in=61,
                        cos_new=1,
                        class_new='yellow'
                    ),
                    dict(
                        dscp_in=50,
                        dscp_new=32,
                        class_new='red'
                    )
                ],
                state='replaced'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_replace_multiple_premark_dscps(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        dscp_in=60,
                        dscp_new=3,
                        cos_new=5,
                        class_new='yellow'
                    ),
                    dict(
                        dscp_in=61,
                        dscp_new=4,
                        cos_new=3,
                        class_new='red'
                    ),
                    dict(
                        dscp_in=63,
                        dscp_new=45,
                        class_new='green'
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "mls qos map premark-dscp 60 to new-dscp 3 new-cos 5 new-bandwidth-class yellow",
            "mls qos map premark-dscp 61 to new-dscp 4 new-cos 3 new-bandwidth-class red",
            "mls qos map premark-dscp 63 to new-dscp 45 new-cos 0 new-bandwidth-class green"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_merge_empty_config_1(self):
        set_module_args(dict(config=None, state='merged'))
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_merge_empty_config_2(self):
        set_module_args(dict(config=[dict(dscp_in=None)], state='merged'))
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_merge_new_config(self):
        set_module_args(dict(config=[dict(dscp_in=60, dscp_new=34, class_new='red', cos_new=3)], state='merged'))
        commands = [
            "mls qos map premark-dscp 60 to new-dscp 34 new-cos 3 new-bandwidth-class red"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_merge_an_existing_config(self):
        set_module_args(dict(config=[dict(dscp_in=63, dscp_new=34, class_new='yellow', cos_new=3)], state='merged'))
        commands = [
            "mls qos map premark-dscp 63 to new-dscp 34 new-cos 3 new-bandwidth-class yellow"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_merge_multiple_premark_dscps(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        dscp_in=60,
                        dscp_new=34,
                        class_new='yellow',
                        cos_new=3
                    ),
                    dict(
                        dscp_in=61,
                        dscp_new=23,
                        class_new='red',
                        cos_new=6
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "mls qos map premark-dscp 60 to new-dscp 34 new-cos 3 new-bandwidth-class yellow",
            "mls qos map premark-dscp 61 to new-dscp 23 new-cos 6 new-bandwidth-class red"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_merge_idempotency_test(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        dscp_in=63,
                        dscp_new=40,
                        cos_new=4,
                        class_new='red'
                    ),
                    dict(
                        dscp_in=34,
                        cos_new=4
                    ),
                    dict(
                        dscp_in=61,
                        cos_new=1,
                        class_new='yellow'
                    ),
                    dict(
                        dscp_in=50,
                        dscp_new=32,
                        class_new='red'
                    )
                ],
                state='merged'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_delete_empty_config_1(self):
        set_module_args(dict(config=None, state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_delete_empty_config_2(self):
        set_module_args(dict(config=[dict(dscp_in=None)], state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_delete_items_in_config(self):
        set_module_args(dict(config=[dict(dscp_in=63, dscp_new=40, cos_new=4)], state='deleted'))
        commands = [
            "mls qos map premark-dscp 63 to new-dscp 63 new-cos 0"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_delete_using_dscp_in(self):
        set_module_args(dict(config=[dict(dscp_in=63)], state='deleted'))
        commands = [
            "no mls qos map premark-dscp 63"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_delete_premark_map_at_default_config_using_dscp_in(self):
        set_module_args(dict(config=[dict(dscp_in=58)], state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_premark_dscps_delete_multiple_premark_maps(self):
        set_module_args(dict(config=[dict(dscp_in=63), dict(dscp_in=34, cos_new=4)], state='deleted'))
        commands = [
            "mls qos map premark-dscp 34 to new-cos 0", "no mls qos map premark-dscp 63"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_override_empty_config_1(self):
        set_module_args(dict(config=None, state='overridden'))
        commands = [
            "no mls qos map premark-dscp 34", "no mls qos map premark-dscp 50",
            "no mls qos map premark-dscp 61", "no mls qos map premark-dscp 63"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_override_empty_config_2(self):
        set_module_args(dict(config=[dict(dscp_in=None)], state='overridden'))
        commands = [
            "no mls qos map premark-dscp 34", "no mls qos map premark-dscp 50",
            "no mls qos map premark-dscp 61", "no mls qos map premark-dscp 63"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_override_an_empty_premark_dscp_map(self):
        set_module_args(dict(config=[dict(dscp_in=62, cos_new=4, class_new='red')], state='overridden'))
        commands = [
            "no mls qos map premark-dscp 34", "no mls qos map premark-dscp 50", "no mls qos map premark-dscp 61",
            "mls qos map premark-dscp 62 to new-cos 4 new-bandwidth-class red", "no mls qos map premark-dscp 63"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_override_a_changed_premark_dscp_map(self):
        set_module_args(dict(config=[dict(dscp_in=63, cos_new=7, class_new='red')], state='overridden'))
        commands = [
            "no mls qos map premark-dscp 34", "no mls qos map premark-dscp 50",
            "no mls qos map premark-dscp 61", "mls qos map premark-dscp 63 to new-dscp 63 new-cos 7"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_premark_dscps_invalid_input_1(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(dscp_in=64, cos_new=8)], state=state))
            self.execute_module(changed=False)

    def test_awplus_premark_dscps_invalid_input_2(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(dscp_in=63, cos_new=8)], state=state))
            self.execute_module(changed=False, failed=True)

    def test_awplus_premark_dscps_invalid_input_3(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(dscp_in=63, cos_new='8')], state=state))
            self.execute_module(changed=False, failed=True)

    def test_awplus_premark_dscps_invalid_input_4(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(dscp_in=63, dscp_new=64)], state=state))
            self.execute_module(changed=False, failed=True)

    def test_awplus_premark_dscps_invalid_input_5(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(dscp_in=63, dscp_new=-1)], state=state))
            self.execute_module(changed=False, failed=True)

    def test_awplus_premark_dscps_invalid_input_6(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(dscp_in=63, class_new='redd')], state=state))
            self.execute_module(changed=False, failed=True)
