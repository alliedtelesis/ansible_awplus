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
from passlib.hash import sha256_crypt

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_vxlan
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusVxlanModule(TestAwplusModule):

    module = awplus_vxlan

    def setUp(self):
        super(TestAwplusVxlanModule, self).setUp()

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
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.vxlan.vxlan.VxlanFacts.get_run_vxlan"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestAwplusVxlanModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_config_config.cfg")
        self.execute_show_command.side_effect = load_from_file

    def test_awplus_vxlan_merge_single(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=10, vni=1000)]), state="merged"))
        commands = [
            "source-interface lo", 
            "host-reachability-protocol evpn-bgp", 
            "nvo vxlan", 
            "map-access vlan 10 vni 1000"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vxlan_merge_mutliple(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=10, vni=1000), dict(vlan=11, vni=2000)]), state="merged"))
        commands = [
            "source-interface lo", 
            "host-reachability-protocol evpn-bgp", 
            "nvo vxlan", 
            "map-access vlan 10 vni 1000",
            "map-access vlan 11 vni 2000"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vxlan_merge_with_existing(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=11, vni=2000)]), state="merged"))
        commands = [
            "nvo vxlan", 
            "no map-access vlan 11",
            "map-access vlan 11 vni 2000"
        ]
        self.execute_module(changed=True, commands=commands, fixture="awplus_config_complete.cfg")

    def test_awplus_vxlan_replace_single(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=10, vni=1000)]), state="replaced"))
        commands = [
            "source-interface lo", 
            "host-reachability-protocol evpn-bgp", 
            "nvo vxlan", 
            "map-access vlan 10 vni 1000"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vxlan_replace_mutliple(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=10, vni=1000), dict(vlan=11, vni=2000)]), state="replaced"))
        commands = [
            "source-interface lo", 
            "host-reachability-protocol evpn-bgp", 
            "nvo vxlan", 
            "map-access vlan 10 vni 1000",
            "map-access vlan 11 vni 2000"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vxlan_replace_with_existing(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=11, vni=2000)]), state="replaced"))
        commands = [
            "nvo vxlan", 
            "no map-access vlan 11",
            "map-access vlan 11 vni 2000"
        ]
        self.execute_module(changed=True, commands=commands, fixture="awplus_config_complete.cfg")

    def test_awplus_vxlan_override_single(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=10, vni=1000)]), state="overridden"))
        commands = [
            "source-interface lo", 
            "host-reachability-protocol evpn-bgp", 
            "nvo vxlan", 
            "map-access vlan 10 vni 1000"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vxlan_override_mutliple(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=10, vni=1000), dict(vlan=11, vni=2000)]), state="overridden"))
        commands = [
            "source-interface lo", 
            "host-reachability-protocol evpn-bgp", 
            "nvo vxlan", 
            "map-access vlan 10 vni 1000",
            "map-access vlan 11 vni 2000"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vxlan_override_existing_with_empty(self):
        set_module_args(dict(config=dict(), state="overridden"))
        commands = [
            "nvo vxlan", 
            "no map-access vlan 10",
            "no map-access vlan 11"
        ]
        self.execute_module(changed=True, commands=commands, fixture="awplus_config_complete.cfg")

    def test_awplus_vxlan_override_existing(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=12, vni=2000)]), state="overridden"))
        commands = [
            "nvo vxlan", 
            "no map-access vlan 10",
            "no map-access vlan 11",
            "map-access vlan 12 vni 2000"
        ]
        self.execute_module(changed=True, commands=commands, fixture="awplus_config_complete.cfg")

    def test_awplus_vxlan_delete_single(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=10)]), state="deleted"))
        commands = [
            "nvo vxlan", 
            "no map-access vlan 10"
        ]
        self.execute_module(changed=True, commands=commands, fixture="awplus_config_complete.cfg")

    def test_awplus_vxlan_delete_mutliple(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=10), dict(vlan=11)]), state="deleted"))
        commands = [
            "nvo vxlan", 
            "no map-access vlan 10",
            "no map-access vlan 11"
        ]
        self.execute_module(changed=True, commands=commands, fixture="awplus_config_complete.cfg")

    def test_awplus_vxlan_delete_non_existing(self):
        set_module_args(dict(config=dict(l2_vnis=[dict(vlan=20)]), state="deleted"))
        commands = []
        self.execute_module(changed=False, commands=commands, fixture="awplus_config_complete.cfg")
