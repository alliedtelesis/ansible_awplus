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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_class_maps
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestClassMapsModule(TestAwplusModule):

    module = awplus_class_maps

    def setUp(self):
        super(TestClassMapsModule, self).setUp()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_execute_show_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.class_maps.class_maps.Class_mapsFacts.get_class_map_conf"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestClassMapsModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_class_maps_show_class_maps_config.cfg")
        self.execute_show_command.side_effect = load_from_file

    def test_awplus_class_maps_replace_empty_config_1(self):
        set_module_args(dict(config=None, state='replaced'))
        self.execute_module(changed=False)

    def test_awplus_class_maps_replace_each_element_in_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='testing',
                        access_group=3001,
                        cos=2,
                        dscp=3,
                        eth_format='802dot2-untagged',
                        eth_protocol='f0',
                        inner_cos=3,
                        inner_vlan=7,
                        ip_precedence=3,
                        mac_type='l2bcast',
                        tcp_flags=dict(
                            ack=True,
                            psh=False,
                            fin=True,
                            syn=True,
                            rst=False,
                            urg=True
                        ),
                        vlan=4050
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "class-map testing", "match access-group 3001", "match cos 2",
            "match dscp 3", "match eth-format 802dot2-untagged protocol f0",
            "match inner-cos 3", "match inner-vlan 7", "match ip-precedence 3",
            "match mac-type l2bcast", "match tcp-flags ack ",
            "no match tcp-flags psh rst ", "match vlan 4050"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_replace_eth_format_only(self):
        set_module_args(dict(config=[dict(name='testing', eth_format='802dot2-tagged')], state='replaced'))
        commands = [
            "class-map testing", "no match tcp-flags fin psh rst syn urg ",
            "no match ip-precedence ", "no match cos ", "no match vlan ",
            "no match mac-type ", "no match inner-vlan ", "no match inner-cos ",
            "no match dscp ", "no match eth-format protocol", "no match access-group 3000"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_replace_out_of_range_1(self):
        set_module_args(dict(config=[dict(name='testing', cos=10)], state='replaced'))
        self.execute_module(changed=False, failed=True)

    def test_awplus_class_maps_replace_out_of_range_2(self):
        set_module_args(dict(config=[dict(name='testing', dscp=100)], state='replaced'))
        self.execute_module(changed=False, failed=True)

    def test_awplus_class_maps_replace_out_of_range_3(self):
        set_module_args(dict(config=[dict(name='testing', inner_vlan=-3)], state='replaced'))
        self.execute_module(changed=False, failed=True)

    def test_awplus_class_maps_replace_2_class_maps(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='testing',
                        mac_type='l2ucast',
                        inner_cos=3,
                        vlan=500,
                        tcp_flags=dict(
                            ack=True,
                            syn=False
                        )
                    ),
                    dict(
                        name='test',
                        dscp=2,
                        ip_precedence=7,
                        access_group=3000
                    )
                ],
                state='replaced'
            )
        )
        commands = [
            "class-map testing", "match inner-cos 3", "match mac-type l2ucast",
            "match tcp-flags ack ", "no match tcp-flags fin psh rst syn urg ",
            "match vlan 500", "no match ip-precedence ", "no match access-group 3000",
            "no match inner-vlan ", "no match cos ", "no match eth-format protocol",
            "no match dscp ", "class-map test", "match access-group 3000",
            "match dscp 2", "match ip-precedence 7"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_replace_nothing_with_class_map(self):
        set_module_args(dict(config=[dict(name='new_class_map')], state='replaced'))
        self.execute_module(changed=False)

    def test_awplus_class_maps_replace_config_with_empty_config(self):
        set_module_args(dict(config=[dict(name='testing')], state='replaced'))
        commands = [
            "class-map testing", "no match inner-vlan ", "no match vlan ",
            "no match cos ", "no match eth-format protocol", "no match access-group 3000",
            "no match tcp-flags fin psh rst syn urg ", "no match mac-type ",
            "no match ip-precedence ", "no match inner-cos ", "no match dscp "
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_replace_empty_config_2(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='testing',
                        access_group=3000,
                        cos=4,
                        dscp=1,
                        eth_format='802dot2-tagged',
                        eth_protocol='0E',
                        inner_cos=1,
                        inner_vlan=5,
                        ip_precedence=7,
                        mac_type='l2mcast',
                        tcp_flags=dict(
                            psh=True,
                            fin=True,
                            syn=True,
                            rst=True,
                            urg=True
                        ),
                        vlan=4090
                    )
                ],
                state='replaced'
            )
        )
        self.execute_module(changed=False)

    def test_awplus_class_maps_replace_with_named_hardware_acl(self):
        set_module_args(dict(config=[dict(name='testing', access_group='named_hardware_acl')], state='replaced'))
        commands = [
            "class-map testing", "match access-group named_hardware_acl",
            "no match mac-type ", "no match inner-cos ", "no match eth-format protocol",
            "no match vlan ", "no match tcp-flags fin psh rst syn urg ", "no match inner-vlan ",
            "no match ip-precedence ", "no match dscp ", "no match cos "
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_empty_config_1(self):
        set_module_args(dict(config=None))
        self.execute_module(changed=False)

    def test_awplus_class_maps_merge_into_existing_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='testing',
                        access_group=3001,
                        cos=7,
                        dscp=2,
                        eth_format='802dot2-untagged',
                        eth_protocol='netbeui',
                        inner_cos=5,
                        inner_vlan=700,
                        ip_precedence=1,
                        mac_type='l2bcast',
                        tcp_flags=dict(
                            ack=True,
                            fin=False,
                            psh=True
                        ),
                        vlan=399
                    )
                ]
            )
        )
        commands = [
            "class-map testing", "match access-group 3001", "match cos 7",
            "match dscp 2", "match eth-format 802dot2-untagged protocol netbeui",
            "match inner-cos 5", "match inner-vlan 700", "match ip-precedence 1",
            "match mac-type l2bcast", "match tcp-flags ack ",
            "no match tcp-flags fin ", "match vlan 399"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_into_existing_empty_config(self):
        set_module_args(dict(config=[dict(name='test', cos=3, dscp=3, inner_cos=3, ip_precedence=3, tcp_flags=dict(ack=False, psh=True))]))
        commands = [
            "class-map test", "match cos 3", "match dscp 3", "match inner-cos 3",
            "match ip-precedence 3", "match tcp-flags psh ", "no match tcp-flags ack "
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_create_new_empty_class_map(self):
        set_module_args(dict(config=[dict(name='new_class_map2')]))
        commands = ["class-map new_class_map2"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_create_new_class_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='new_class_map2',
                        cos=3,
                        dscp=3,
                        eth_format='802dot2-untagged',
                        eth_protocol='netbeui',
                        tcp_flags=dict(
                            syn=True
                        )
                    )
                ]
            )
        )
        commands = [
            "class-map new_class_map2", "match eth-format 802dot2-untagged protocol netbeui",
            "match cos 3", "match dscp 3", "match tcp-flags syn "
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_multiple_class_maps(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='test',
                        cos=5,
                        access_group=3000,
                        mac_type='l2mcast'
                    ),
                    dict(
                        name='new_class_map',
                        inner_cos=3,
                        tcp_flags=dict(
                            psh=True
                        ),
                        vlan=302
                    )
                ]
            )
        )
        commands = [
            "class-map test", "match access-group 3000", "match cos 5",
            "match mac-type l2mcast", "class-map new_class_map",
            "match inner-cos 3", "match tcp-flags psh ", "match vlan 302"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_new_class_map_with_only_eth_protocol(self):
        set_module_args(dict(config=[dict(name='new_class_map', eth_protocol='0E')]))
        commands = ["class-map new_class_map"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_with_only_eth_protocol(self):
        set_module_args(dict(config=[dict(name='testing', eth_protocol='0E')]))
        self.execute_module(changed=False)

    def test_awplus_class_maps_merge_same_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='testing',
                        access_group=3000,
                        cos=4,
                        dscp=1,
                        eth_format='802dot2-tagged',
                        eth_protocol='0E',
                        inner_cos=1,
                        inner_vlan=5,
                        ip_precedence=7,
                        mac_type='l2mcast',
                        tcp_flags=dict(
                            ack=False,
                            fin=True,
                            psh=True,
                            rst=True,
                            syn=True,
                            urg=True
                        )
                    )
                ]
            )
        )
        self.execute_module(changed=False)

    def test_awplus_class_maps_tcp_flags(self):
        set_module_args(dict(config=[dict(name='testing', tcp_flags=dict(ack=True, syn=True, fin=False, psh=False))]))
        commands = ["class-map testing", "match tcp-flags ack ", "no match tcp-flags fin psh "]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_named_hardware_acl(self):
        set_module_args(dict(config=[dict(name='test', access_group='named_hardware_acl')]))
        commands = ["class-map test", "match access-group named_hardware_acl"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_merge_different_hardware_acl(self):
        set_module_args(dict(config=[dict(name='testing', access_group='named_hardware_acl')]))
        commands = ["class-map testing", "match access-group named_hardware_acl"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_delete_empty_config_1(self):
        set_module_args(dict(config=None, state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_class_maps_delete_class_map_with_name(self):
        set_module_args(dict(config=[dict(name='testing')], state='deleted'))
        commands = ["no class-map testing"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_delete_non_existing_class_map_with_name(self):
        set_module_args(dict(config=[dict(name='class-map')], state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_class_maps_delete_multiple_class_maps_with_name_1(self):
        set_module_args(dict(config=[dict(name='testing'), dict(name='test')], state='deleted'))
        commands = ["no class-map testing", "no class-map test"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_delete_multiple_class_maps_with_name_2(self):
        set_module_args(dict(config=[dict(name='testing'), dict(name='not-real-class-map')], state='deleted'))
        commands = ["no class-map testing"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_delete_all_elements_in_class_map(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='testing',
                        access_group=3000,
                        cos=4,
                        dscp=1,
                        eth_format='802dot2-tagged',
                        eth_protocol='0E',
                        inner_cos=1,
                        inner_vlan=5,
                        ip_precedence=7,
                        mac_type='l2mcast',
                        tcp_flags=dict(
                            ack=False,
                            fin=False,
                            psh=False,
                            rst=False,
                            syn=False,
                            urg=False
                        ),
                        vlan=4090
                    )
                ],
                state='deleted'
            )
        )
        commands = [
            "class-map testing", "no match access-group 3000", "no match cos",
            "no match dscp", "no match eth-format protocol", "no match inner-cos",
            "no match inner-vlan", "no match ip-precedence", "no match mac-type",
            "no match tcp-flags urg psh rst syn fin ", "no match vlan"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_delete_elements_in_multiple_class_maps(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='testing',
                        access_group=3000,
                        inner_cos=4,
                        tcp_flags=dict(
                            ack=False,
                            syn=False
                        )
                    ),
                    dict(
                        name='test'
                    )
                ],
                state='deleted'
            )
        )
        commands = [
            "class-map testing", "no match access-group 3000",
            "no match tcp-flags syn ", "no class-map test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_delete_element_with_invalid_eth_format(self):
        set_module_args(dict(config=[dict(name='testing', eth_format='ethii-tagged')], state='deleted'))
        self.execute_module(changed=False)

    def test_awplus_class_maps_delete_element_with_only_eth_format(self):
        set_module_args(dict(config=[dict(name='testing', eth_format='802dot2-tagged')], state='deleted'))
        commands = ["class-map testing", "no match eth-format protocol"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_override_with_empty_config_1(self):
        set_module_args(dict(config=None, state='overridden'))
        commands = ["no class-map test", "no class-map testing"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_override_existing_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='testing',
                        inner_cos=4,
                        inner_vlan=7,
                        mac_type='l2bcast',
                        ip_precedence=1,
                        vlan=3
                    )
                ],
                state='overridden'
            )
        )
        commands = [
            "class-map testing", "match inner-cos 4", "match inner-vlan 7",
            "match ip-precedence 1", "match mac-type l2bcast", "match vlan 3",
            "no match tcp-flags fin psh rst syn urg ", "no match eth-format protocol",
            "no match cos ", "no match access-group 3000", "no match dscp ",
            "no class-map test"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_override_existing_config(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='new-class-map',
                        cos=3,
                        vlan=3,
                        tcp_flags=dict(
                            ack=True,
                            syn=True,
                            urg=True
                        )
                    )
                ],
                state='overridden'
            )
        )
        commands = [
            "no class-map testing", "no class-map test", "class-map new-class-map",
            "match cos 3", "match vlan 3", "match tcp-flags ack syn urg "
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_class_maps_override_multiple_class_maps(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name='new-class-map',
                        mac_type='l2ucast',
                        tcp_flags=dict(
                            fin=True
                        )
                    ),
                    dict(
                        name='test',
                        inner_cos=5,
                        vlan=390
                    )
                ],
                state='overridden'
            )
        )
        commands = [
            "no class-map testing", "class-map test", "match inner-cos 5", "match vlan 390",
            "class-map new-class-map", "match mac-type l2ucast", "match tcp-flags fin "
        ]
        self.execute_module(changed=True, commands=commands)
