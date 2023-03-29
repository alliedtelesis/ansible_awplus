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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_policy_maps
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestPolicyMapsModule(TestAwplusModule):

    module = awplus_policy_maps

    def setUp(self):
        super(TestPolicyMapsModule, self).setUp()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_execute_show_policy_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.policy_maps.policy_maps.Policy_mapsFacts.get_policy_map_conf"
        )
        self.execute_show_policy_command = self.mock_execute_show_policy_command.start()

        self.mock_execute_show_pol_class_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.policy_maps."
            "policy_maps.Policy_mapsFacts.get_policy_class_map_conf"
        )
        self.execute_show_pol_classes_command = self.mock_execute_show_pol_class_command.start()

        self.mock_check_classes = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.policy_maps.policy_maps.Policy_maps.check_classes"
        )
        self.check_classes = self.mock_check_classes.start()

    def tearDown(self):
        super(TestPolicyMapsModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_execute_show_policy_command.stop()
        self.mock_execute_show_pol_class_command.stop()
        self.mock_check_classes.stop()

    def load_fixtures(self, commands=None):
        def load_policy_from_file(*args, **kwargs):
            result = load_fixture("awplus_policy_maps_get_policy_config.cfg")
            return result

        def load_policy_class_from_file(*args, **kwargs):
            result = load_fixture("awplus_policy_maps_get_class_config.cfg")
            return result
        self.execute_show_policy_command.side_effect = load_policy_from_file
        self.execute_show_pol_classes_command.side_effect = load_policy_class_from_file
        self.check_classes.return_value = True

    def test_awplus_policy_maps_replace_empty_config_1(self):
        set_module_args(dict(config=None, state='replaced'))
        self.execute_module(changed=False)

    def test_awplus_policy_maps_replace_empty_config_2(self):
        set_module_args(dict(config=[dict(name=None, classifiers=None)], state='replaced'))
        self.execute_module(changed=False)

    def test_awplus_policy_maps_replace_some_of_full_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='new description',
                        classifiers=[
                            dict(
                                name='test',
                                remark_map=[
                                    dict(
                                        new_dscp=63,
                                        new_class='red',
                                        class_in='yellow'
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "policy-map test_pol_map", "no trust", "description new description", "default-action permit", "class test",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class yellow to new-dscp 63 new-bandwidth-class red", "storm-downtime 10",
            "no remark new-cos external",
            "no set ip next-hop", "no police", "no storm-protection", "no storm-window",
            "no storm-rate", "no storm-action", "no class testing"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_replace_multiple_classes(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='new description',
                        classifiers=[
                            dict(
                                name='test',
                                remark_map=[
                                    dict(
                                        new_dscp=63,
                                        new_class='red',
                                        class_in='yellow'
                                    )
                                ]
                            ),
                            dict(
                                name='testing',
                                policer=dict(
                                    action='drop_red',
                                    type='twin_rate',
                                    cir=128,
                                    cbs=4096,
                                    pbs=4096,
                                    pir=3264
                                )
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "policy-map test_pol_map", "no trust", "description new description", "default-action permit",
            "class test", "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class yellow to new-dscp 63 new-bandwidth-class red", "storm-downtime 10",
            "no remark new-cos external", "no set ip next-hop", "no police", "no storm-protection", "no storm-window",
            "no storm-rate", "no storm-action", "class testing", "police twin-rate 128 3264 4096 4096 action drop-red",
            "storm-downtime 10", "no remark new-cos both",
            "no remark-map bandwidth-class green to new-dscp new-bandwidth-class",
            "no remark-map bandwidth-class red to new-dscp new-bandwidth-class"

        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_delete_everything_with_replace_1(self):
        set_module_args(dict(config=[dict(name='test_pol_map')], state='replaced'))
        commands = [
            "policy-map test_pol_map", "no description", "no trust",
            "default-action permit", "no class test", "no class testing"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_delete_everything_with_replace_2(self):
        set_module_args(dict(config=[dict(name='test_pol_map', classifiers=[dict(name='test')])], state='replaced'))
        commands = [
            "policy-map test_pol_map", "no description", "no trust", "default-action permit",
            "class test", "storm-downtime 10", "no remark new-cos external",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "no set ip next-hop", "no police", "no storm-protection", "no storm-window",
            "no storm-rate", "no storm-action", "no class testing"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_replace_everything_1(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='new description',
                        trust_dscp=False,
                        default_action='copy_to_cpu',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=4,
                                    apply='both'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='red',
                                        new_dscp=32,
                                        new_class='yellow'
                                    )
                                ],
                                policer=dict(
                                    type='single_rate',
                                    cir=100,
                                    cbs=4096,
                                    ebs=4096,
                                    action='remark_transmit'
                                ),
                                storm_action='link_down',
                                storm_downtime=200,
                                storm_rate=200,
                                storm_window=500,
                                storm_protection=False,
                                pbr_next_hop='172.153.43.2'
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "policy-map test_pol_map", "no trust", "description new description",
            "default-action copy-to-cpu", "class test", "remark new-cos 4 both",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class red to new-dscp 32 new-bandwidth-class yellow",
            "police single-rate 128 4096 4096 action remark-transmit", "storm-action linkdown",
            "storm-downtime 200", "storm-rate 200", "storm-window 500", "no storm-protection",
            "set ip next-hop 172.153.43.2", "no class testing"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_replace_everything_2(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='new description',
                        trust_dscp=False,
                        default_action='copy_to_cpu',
                        classifiers=[
                            dict(
                                name='testing',
                                remark=dict(
                                    new_cos=4,
                                    apply='both'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='red',
                                        new_dscp=32,
                                        new_class='yellow'
                                    )
                                ],
                                policer=dict(
                                    type='single_rate',
                                    cir=100,
                                    cbs=4096,
                                    ebs=4096,
                                    action='remark_transmit'
                                ),
                                storm_action='link_down',
                                storm_downtime=200,
                                storm_rate=200,
                                storm_window=500,
                                storm_protection=False,
                                pbr_next_hop='172.153.43.2'
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "policy-map test_pol_map", "no trust", "description new description",
            "default-action copy-to-cpu", "class testing", "remark new-cos 4 both",
            "no remark-map bandwidth-class green to new-dscp new-bandwidth-class",
            "no remark-map bandwidth-class red to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class red to new-dscp 32 new-bandwidth-class yellow",
            "police single-rate 128 4096 4096 action remark-transmit", "storm-action linkdown",
            "storm-downtime 200", "storm-rate 200", "storm-window 500",
            "set ip next-hop 172.153.43.2", "no class test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_replace_idempotency_test(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='testing the tester 123',
                        trust_dscp=True,
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='external'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_dscp=40,
                                        new_class='green'
                                    )
                                ],
                                policer=dict(
                                    type='twin_rate',
                                    cir=120,
                                    cbs=40,
                                    pbs=409,
                                    pir=3250,
                                    action='drop_red'
                                ),
                                storm_action='port_disable',
                                storm_downtime=100,
                                storm_rate=20,
                                storm_window=400,
                                storm_protection=True,
                                pbr_next_hop='192.172.168.3'
                            ),
                            dict(
                                name='testing',
                                remark=dict(
                                    new_cos=7,
                                    apply='both'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='green',
                                        new_dscp=63,
                                        new_class='red'
                                    ),
                                    dict(
                                        class_in='red',
                                        new_dscp=1,
                                        new_class='yellow'
                                    )
                                ],
                                storm_downtime=350
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_policy_maps_replace_nothing_with_non_existent_policy_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='non-existing-pol-map',
                        description='traffic',
                        trust_dscp=True,
                        classifiers=[
                            dict(
                                name='non-existing-class',
                                storm_downtime=40
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_policy_maps_replace_delete_change_config_with_none_and_0(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='testing the tester 123',
                        trust_dscp=True,
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='none'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_dscp=5,
                                        new_class='none'
                                    )
                                ],
                                policer=dict(
                                    type='none',
                                    cir=128,
                                    cbs=4096,
                                    pbs=4096,
                                    pir=3264,
                                    action='drop_red'
                                ),
                                storm_action='none',
                                storm_downtime=0,
                                storm_rate=0,
                                storm_window=0,
                                pbr_next_hop='none'
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "policy-map test_pol_map", "class test", "no remark new-cos external",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class yellow to new-dscp 5 ", "no police",
            "no storm-action", "no storm-downtime", "no storm-rate", "no storm-window",
            "no set ip next-hop", "no storm-protection", "no storm-downtime", "no class testing"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_replace_delete_change_empty_config_with_none_and_0(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test',
                        description='testing the tester 123',
                        trust_dscp=True,
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='none'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_dscp=5,
                                        new_class='none'
                                    )
                                ],
                                policer=dict(
                                    type='none',
                                    cir=128,
                                    cbs=4096,
                                    pbs=4096,
                                    pir=3264,
                                    action='drop_red'
                                ),
                                storm_action='none',
                                storm_downtime=0,
                                storm_rate=0,
                                storm_window=0,
                                pbr_next_hop='none'
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "policy-map test", "description testing the tester 123", "trust dscp", "default-action deny",
            "class test", "remark-map bandwidth-class yellow to new-dscp 5 ", "no class tester"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_empty_config_1(self):
        set_module_args(dict(config=None, state='merged'))
        self.execute_module(changed=False)

    def test_awplus_policy_maps_merge_empty_config_2(self):
        set_module_args(dict(config=[dict(name=None, classifiers=None)], state='merged'))
        self.execute_module(changed=False)

    def test_awplus_policy_maps_merge_new_policy_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test2',
                        description='merging the config',
                        trust_dscp=True,
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='tester',
                                remark=dict(
                                    new_cos=5,
                                    apply='both'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='red',
                                        new_dscp=3,
                                        new_class='green'
                                    )
                                ],
                                policer=dict(
                                    type='single_rate',
                                    cir=100,
                                    cbs=100,
                                    ebs=100,
                                    action='remark_transmit'
                                ),
                                storm_protection=True,
                                storm_action='port_disable',
                                storm_downtime=200,
                                storm_rate=100,
                                storm_window=500,
                                pbr_next_hop='192.192.92.0'
                            )
                        ]
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "policy-map test2", "trust dscp ", "description merging the config", "default-action deny",
            "class tester", "remark new-cos 5 both", "remark-map bandwidth-class red to new-dscp 3  new-bandwidth-class green",
            "police single-rate 128 4096 4096 action remark-transmit", "storm-protection ", "storm-action portdisable",
            "storm-downtime 200", "storm-rate 100", "storm-window 500", "set ip next-hop 192.192.92.0"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_modify_elements_in_existing_policy_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='merging a new description',
                        trust_dscp=True,
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='testing',
                                remark=dict(
                                    new_cos=5,
                                    apply='both'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='red',
                                        new_dscp=3,
                                        new_class='green'
                                    )
                                ],
                                policer=dict(
                                    type='single_rate',
                                    cir=100,
                                    cbs=100,
                                    ebs=100,
                                    action='remark_transmit'
                                ),
                                storm_protection=True,
                                storm_action='vlan_disable',
                                storm_downtime=200,
                                storm_rate=100,
                                storm_window=500,
                                pbr_next_hop='192.192.92.0'
                            )
                        ]
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "policy-map test_pol_map", "description merging a new description", "class testing",
            "remark new-cos 5 both", "remark-map bandwidth-class red to new-dscp 3  new-bandwidth-class green",
            "police single-rate 128 4096 4096 action remark-transmit", "storm-protection ",
            "storm-action vlandisable", "storm-downtime 200", "storm-rate 100",
            "storm-window 500", "set ip next-hop 192.192.92.0"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_idempotency_test(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='testing the tester 123',
                        trust_dscp=True,
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='external'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_dscp=40,
                                        new_class='green'
                                    )
                                ],
                                policer=dict(
                                    type='twin_rate',
                                    cir=120,
                                    cbs=40,
                                    pbs=409,
                                    pir=3250,
                                    action='drop_red'
                                ),
                                storm_action='port_disable',
                                storm_downtime=100,
                                storm_rate=20,
                                storm_window=400,
                                storm_protection=True,
                                pbr_next_hop='192.172.168.3'
                            ),
                            dict(
                                name='testing',
                                remark=dict(
                                    new_cos=7,
                                    apply='both'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='green',
                                        new_dscp=63,
                                        new_class='red'
                                    ),
                                    dict(
                                        class_in='red',
                                        new_dscp=1,
                                        new_class='yellow'
                                    )
                                ],
                                storm_downtime=350
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_policy_maps_merge_storm_parameters_before_storm_protection(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        classifiers=[
                            dict(
                                name='testing',
                                storm_action='vlan_disable',
                                storm_downtime=200,
                                storm_rate=100,
                                storm_window=500,
                                storm_protection=True
                            )
                        ]
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "policy-map test_pol_map", "default-action permit", "class testing", "storm-action vlandisable",
            "storm-downtime 200", "storm-rate 100", "storm-window 500", "storm-protection "
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_multiple_classes(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        classifiers=[
                            dict(
                                name='testing',
                                storm_action='vlan_disable'
                            ),
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=3,
                                    apply='internal'
                                )
                            ),
                            dict(
                                name='tester',
                                policer=dict(
                                    type='twin_rate',
                                    cir=1000000,
                                    cbs=5000,
                                    pir=10231,
                                    pbs=201232,
                                    action='remark_transmit'
                                )
                            )
                        ]
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "policy-map test_pol_map", "default-action permit", "class testing",
            "storm-action vlandisable", "class test", "remark new-cos 3 internal",
            "class tester", "police twin-rate 1000000 10240 4096 200704 action remark-transmit"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_new_policy_map_class_name_only(self):
        set_module_args(dict(config=[dict(name='new_pol_map', classifiers=[dict(name='tester')])], state='merged'))
        commands = [
            "policy-map new_pol_map", "default-action permit", "class tester"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_new_policy_map_no_class(self):
        set_module_args(dict(config=[dict(name='new_pol_map', description='a new description')], state='merged'))
        commands = [
            "policy-map new_pol_map", "default-action permit", "description a new description"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_delete_change_with_merged(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='none'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_dscp=-1,
                                        new_class='green'
                                    )
                                ],
                                policer=dict(
                                    type='none',
                                    cir=128,
                                    cbs=4096,
                                    pbs=10000,
                                    pir=3264,
                                    action='drop_red'
                                ),
                                storm_action='none',
                                storm_downtime=0,
                                storm_rate=0,
                                storm_window=0,
                                pbr_next_hop='none'
                            )
                        ]
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "policy-map test_pol_map", "default-action permit", "class test", "no remark new-cos  external",
            "remark-map bandwidth-class yellow  to new-bandwidth-class green", "no police",
            "no storm-action", "storm-downtime 10", "no storm-rate", "no storm-window",
            "no set ip next-hop "
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_delete_change_with_merged_with_empty_class(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='none'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='red',
                                        new_dscp=2,
                                        new_class='none'
                                    )
                                ],
                                policer=dict(
                                    type='none',
                                    cir=128,
                                    cbs=4096,
                                    pbs=10000,
                                    pir=3264,
                                    action='drop_red'
                                ),
                                storm_action='none',
                                storm_downtime=0,
                                storm_rate=0,
                                storm_window=0,
                                pbr_next_hop='none'
                            )
                        ]
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "policy-map test", "class test", "remark-map bandwidth-class red to new-dscp 2 "
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_delete_empty_config_1(self):
        set_module_args(dict(config=None, state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_policy_maps_delete_empty_config_2(self):
        set_module_args(dict(config=[dict(name=None, classifiers=None)], state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_policy_maps_delete_everything_in_policy_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='testing the tester 123',
                        trust_dscp=True,
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='external'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_dscp=40,
                                        new_class='green'
                                    )
                                ],
                                policer=dict(
                                    type='twin_rate',
                                    cir=120,
                                    cbs=40,
                                    pbs=409,
                                    pir=3250,
                                    action='drop_red'
                                ),
                                storm_action='port_disable',
                                storm_downtime=100,
                                storm_rate=20,
                                storm_window=400,
                                storm_protection=True,
                                pbr_next_hop='192.172.168.3'
                            ),
                            dict(
                                name='testing'
                            )
                        ]
                    )
                ],
                state='deleted'
            )
        )
        commands = [
            "policy-map test_pol_map", "no trust ", "no description ", "default-action permit",
            "class test", "storm-downtime 10", "no remark new-cos external",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "no set ip next-hop", "no police", "no storm-protection", "no storm-window",
            "no storm-rate", "no storm-action", "no class testing"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_delete_items_in_multiple_classes(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        classifiers=[
                            dict(
                                name='testing',
                                remark_map=[
                                    dict(
                                        class_in='green',
                                        new_dscp=63,
                                        new_class='red'
                                    )
                                ]
                            ),
                            dict(
                                name='test',
                                pbr_next_hop='192.172.168.3',
                                policer=dict(
                                    action='drop_red',
                                    cbs=5000,
                                    cir=140,
                                    pbs=4050,
                                    pir=3270,
                                    type='twin_rate'
                                )
                            )
                        ]
                    )
                ],
                state='deleted'
            )
        )
        commands = [
            "policy-map test_pol_map", "class testing",
            "no remark-map bandwidth-class green to new-dscp new-bandwidth-class",
            "class test", "no set ip next-hop", "no police"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_delete_from_non_existing_pol_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='pol_map',
                        description='something descriptive',
                        default_action='copy_to_mirror',
                        classifiers=[
                            dict(
                                name='class',
                                pbr_next_hop='192.172.168.3'
                            )
                        ]
                    )
                ],
                state='deleted'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_policy_maps_delete_config_that_doenst_fully_match_have(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='something differant from have',
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='testing',
                                remark=dict(
                                    apply='external',
                                    new_cos=7
                                ),
                                remark_map=[
                                    dict(
                                        class_in='green',
                                        new_class='red',
                                        new_dscp=60
                                    ),
                                    dict(
                                        class_in='red',
                                        new_class='yellow',
                                        new_dscp=1
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state='deleted'
            )
        )
        commands = [
            "policy-map test_pol_map", "default-action permit", "class testing",
            "no remark-map bandwidth-class red to new-dscp new-bandwidth-class"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_delete_items_in_config_using_none_0__1(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    apply='none',
                                    new_cos=2
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_class='none',
                                        new_dscp=40
                                    )
                                ],
                                policer=dict(
                                    type='none',
                                    cir=128,
                                    cbs=4096,
                                    pbs=4096,
                                    pir=3264
                                ),
                                storm_action='none',
                                storm_downtime=0,
                                storm_rate=0,
                                storm_window=0,
                                pbr_next_hop='none'
                            )
                        ]
                    )
                ],
                state='deleted'
            )
        )
        commands = [
            "policy-map test_pol_map", "class test", "storm-downtime 10", "no remark new-cos external",
            "no set ip next-hop", "no police", "no storm-window", "no storm-rate", "no storm-action"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_delete_items_in_empty_config_using_none_0__1(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    apply='none',
                                    new_cos=2
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_class='none',
                                        new_dscp=40
                                    )
                                ],
                                policer=dict(
                                    type='none',
                                    cir=128,
                                    cbs=4096,
                                    pbs=4096,
                                    pir=3264
                                ),
                                storm_action='none',
                                storm_downtime=0,
                                storm_rate=0,
                                storm_window=0,
                                pbr_next_hop='none'
                            )
                        ]
                    )
                ],
                state='deleted'
            )
        )
        commands = [
            "policy-map test", "default-action permit", "no class test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_delete_class_with_name(self):
        set_module_args(dict(config=[dict(name='test_pol_map', classifiers=[dict(name='testing')])], state='deleted'))
        commands = [
            "policy-map test_pol_map", "no class testing"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_override_empty_config_1(self):
        set_module_args(dict(config=None, state='overridden'))
        commands = [
            "no policy-map test_pol_map", "no policy-map test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_override_empty_config_2(self):
        set_module_args(dict(config=[dict(name=None, classifiers=None)], state='overridden'))
        commands = [
            "no policy-map test", "no policy-map test_pol_map"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_override_with_new_policy_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='new_pol_map',
                        description='something something 123',
                        default_action='send_to_mirror',
                        classifiers=[
                            dict(
                                name='tester',
                                policer=dict(
                                    type='single_rate',
                                    cir=3421,
                                    cbs=122332,
                                    ebs=231314,
                                    action='remark_transmit'
                                )
                            )
                        ]
                    )
                ],
                state='overridden'
            )
        )
        commands = [
            "no policy-map test", "no policy-map test_pol_map", "policy-map new_pol_map",
            "description something something 123", "default-action send-to-mirror", "class tester",
            "police single-rate 3392 122880 229376 action remark-transmit"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_override_existing_policy_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        description='a differant description',
                        default_action='send_to_mirror',
                        classifiers=[
                            dict(
                                name='tester',
                                policer=dict(
                                    type='single_rate',
                                    cir=3421,
                                    cbs=122332,
                                    ebs=231314,
                                    action='remark_transmit'
                                )
                            ),
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='internal'
                                ),
                                storm_rate=23525
                            )
                        ]
                    )
                ],
                state='overridden'
            )
        )
        commands = [
            "policy-map test_pol_map", "no trust", "description a differant description", "default-action send-to-mirror",
            "class tester", "police single-rate 3392 122880 229376 action remark-transmit", "storm-downtime 10",
            "class test", "remark new-cos 2 internal", "storm-rate 23525", "storm-downtime 10",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class", "no set ip next-hop",
            "no police", "no storm-protection", "no storm-window", "no storm-action",
            "no class testing", "no policy-map test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_override_idempotency_test(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test',
                        classifiers=[
                            dict(
                                name='tester'
                            )
                        ]
                    ),
                    dict(
                        name='test_pol_map',
                        description='testing the tester 123',
                        trust_dscp=True,
                        default_action='deny',
                        classifiers=[
                            dict(
                                name='test',
                                remark=dict(
                                    new_cos=2,
                                    apply='external'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_dscp=40,
                                        new_class='green'
                                    )
                                ],
                                policer=dict(
                                    type='twin_rate',
                                    cir=120,
                                    cbs=40,
                                    pbs=409,
                                    pir=3250,
                                    action='drop_red'
                                ),
                                storm_action='port_disable',
                                storm_downtime=100,
                                storm_rate=20,
                                storm_window=400,
                                storm_protection=True,
                                pbr_next_hop='192.172.168.3'
                            ),
                            dict(
                                name='testing',
                                remark=dict(
                                    new_cos=7,
                                    apply='both'
                                ),
                                remark_map=[
                                    dict(
                                        class_in='green',
                                        new_dscp=63,
                                        new_class='red'
                                    ),
                                    dict(
                                        class_in='red',
                                        new_dscp=1,
                                        new_class='yellow'
                                    )
                                ],
                                storm_downtime=350
                            )
                        ]
                    )
                ],
                state='overridden'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_policy_maps_test_rounding_of_policer_1(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        classifiers=[
                            dict(
                                name='testing',
                                policer=dict(
                                    type='single_rate',
                                    cir=10,
                                    cbs=16767373,
                                    ebs=293,
                                    action='drop_red'
                                )
                            )
                        ]
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "policy-map test_pol_map", "default-action permit", "class testing",
            "police single-rate 64 16769024 4096 action drop-red"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_test_rounding_of_policer_2(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        classifiers=[
                            dict(
                                name='testing',
                                policer=dict(
                                    type='twin_rate',
                                    cir=10,
                                    cbs=431,
                                    pbs=2353674,
                                    pir=342541,
                                    action='remark_transmit'
                                )
                            )
                        ]
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "policy-map test_pol_map", "no trust", "no description",
            "default-action permit", "class testing",
            "police twin-rate 64 342528 4096 2355200 action remark-transmit",
            "storm-downtime 10", "no remark new-cos both",
            "no remark-map bandwidth-class green to new-dscp new-bandwidth-class",
            "no remark-map bandwidth-class red to new-dscp new-bandwidth-class",
            "no class test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_merge_multiple_remark_maps(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test_pol_map',
                        classifiers=[
                            dict(
                                name='test',
                                remark_map=[
                                    dict(
                                        class_in='yellow',
                                        new_dscp=45,
                                        new_class='green'
                                    ),
                                    dict(
                                        class_in='green',
                                        new_dscp=32,
                                        new_class='red'
                                    ),
                                    dict(
                                        class_in='yellow',
                                        new_dscp=40,
                                        new_class='red'
                                    ),
                                    dict(
                                        class_in='red',
                                        new_dscp='4',
                                        new_class='red'
                                    ),
                                    dict(
                                        class_in='red',
                                        new_dscp=43,
                                        new_class='yellow'
                                    )
                                ]
                            )
                        ]
                    )
                ],
                state='merged'
            )
        )
        commands = [
            "policy-map test_pol_map", "default-action permit", "class test",
            "remark-map bandwidth-class yellow to new-dscp 45  new-bandwidth-class green",
            "remark-map bandwidth-class green to new-dscp 32  new-bandwidth-class red",
            "remark-map bandwidth-class yellow to new-dscp 40  new-bandwidth-class red",
            "remark-map bandwidth-class red to new-dscp 4  new-bandwidth-class red",
            "remark-map bandwidth-class red to new-dscp 43  new-bandwidth-class yellow"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_policy_maps_invalid_values_test_1(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(
                dict(
                    config=[
                        dict(
                            name='test_pol_map',
                            classifiers=[
                                dict(
                                    name='test',
                                    remark=dict(
                                        new_cos=9,
                                        apply='internal'
                                    )
                                )
                            ]
                        )
                    ],
                    state=state
                )
            )
            self.execute_module(changed=False, failed=True)

    def test_awplus_policy_maps_invalid_values_test_2(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(
                dict(
                    config=[
                        dict(
                            name='test_pol_map',
                            classifiers=[
                                dict(
                                    name='test',
                                    policer=dict(
                                        type='single_rate',
                                        cir=1000000000,
                                        cbs=231,
                                        ebs=2432,
                                        action='drop_red'
                                    )
                                )
                            ]
                        )
                    ],
                    state=state
                )
            )
            self.execute_module(changed=False, failed=True)

    def test_awplus_policy_maps_invalid_values_test_3(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(
                dict(
                    config=[
                        dict(
                            name='test_pol_map',
                            classifiers=[
                                dict(
                                    name='test',
                                    policer=dict(
                                        cir=100,
                                        cbs=231,
                                        ebs=2432,
                                        action='drop_red'
                                    )
                                )
                            ]
                        )
                    ],
                    state=state
                )
            )
            self.execute_module(changed=False, failed=True)

    def test_awplus_policy_maps_invalid_values_test_4(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(
                dict(
                    config=[
                        dict(
                            name='test_pol_map',
                            classifiers=[
                                dict(
                                    name='test',
                                    remark_map=[
                                        dict(
                                            new_dscp=75,
                                            new_class='green',
                                            class_in='red'
                                        )
                                    ]
                                )
                            ]
                        )
                    ],
                    state=state
                )
            )
            self.execute_module(changed=False, failed=True)

    def test_awplus_policy_maps_invalid_values_test_5(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(name='test_pol_map', classifiers=[dict(name='test', remark_map=[dict(new_dscp=33)])])], state=state))
            self.execute_module(changed=False, failed=True)

    def test_awplus_policy_maps_invalid_values_test_6(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(
                dict(
                    config=[
                        dict(
                            name='test_pol_map',
                            classifiers=[
                                dict(
                                    name='test',
                                    remark_map=[
                                        dict(
                                            new_dscp=33,
                                            new_class='green',
                                            class_in='red'
                                        ),
                                        dict(
                                            new_dscp=64,
                                            new_class='green',
                                            class_in='red'
                                        )
                                    ]
                                )
                            ]
                        )
                    ],
                    state=state
                )
            )
            self.execute_module(changed=False, failed=True)

    def test_awplus_policy_maps_invalid_values_test_7(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(name='test_pol_map', classifiers=[dict(name='test', storm_downtime=90000)])], state=state))
            self.execute_module(changed=False, failed=True)

    def test_awplus_policy_maps_invalid_values_test_8(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(name='test_pol_map', classifiers=[dict(name='test', storm_rate=40000001)])], state=state))
            self.execute_module(changed=False, failed=True)

    def test_awplus_policy_maps_invalid_values_test_9(self):
        states = ('merged', 'replaced', 'deleted')
        for state in states:
            set_module_args(dict(config=[dict(name='test_pol_map', classifiers=[dict(name='test', storm_window=50)])], state=state))
            self.execute_module(changed=False, failed=True)
