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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_mlag
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusMlagModule(TestAwplusModule):

    module = awplus_mlag

    def setUp(self):
        super(TestAwplusMlagModule, self).setUp()

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
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.mlag.mlag.MlagFacts.get_run_mlag"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestAwplusMlagModule, self).tearDown()
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

    def test_awplus_mlag_merge_all_existing(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
                source_address="1.1.1.2",
                session_timeout="60",
                keepalive_interval="2"
            )]), state="merged"))
        commands = [
            "mlag domain 10",
            "peer-link port1.0.10",
            "peer-address 1.1.1.1",
            "source-address 1.1.1.2",
            "session-timeout 60",
            "keepalive-interval 2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_merge_all_new(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=11,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
                source_address="1.1.1.2",
                session_timeout="60",
                keepalive_interval="2"
            )]), state="merged"))
        commands = [
            "no mlag domain 10",
            "mlag domain 11",
            "peer-link port1.0.10",
            "peer-address 1.1.1.1",
            "source-address 1.1.1.2",
            "session-timeout 60",
            "keepalive-interval 2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_merge_partial_existing(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
            )]), state="merged"))
        commands = [
            "mlag domain 10",
            "peer-link port1.0.10",
            "peer-address 1.1.1.1",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_merge_partial_new(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=11,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
            )]), state="merged"))
        commands = [
            "no mlag domain 10",
            "mlag domain 11",
            "peer-link port1.0.10",
            "peer-address 1.1.1.1",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_merge_defaults(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                session_timeout="30",
                keepalive_interval="1"
            )]), state="merged"))
        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_awplus_mlag_replace_all_existing(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
                source_address="1.1.1.2",
                session_timeout="60",
                keepalive_interval="2"
            )]), state="replaced"))
        commands = [
            "mlag domain 10",
            "peer-link port1.0.10",
            "peer-address 1.1.1.1",
            "source-address 1.1.1.2",
            "session-timeout 60",
            "keepalive-interval 2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_replace_all_new(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=11,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
                source_address="1.1.1.2",
                session_timeout="60",
                keepalive_interval="2"
            )]), state="replaced"))
        commands = [
            "no mlag domain 10",
            "mlag domain 11",
            "peer-link port1.0.10",
            "peer-address 1.1.1.1",
            "source-address 1.1.1.2",
            "session-timeout 60",
            "keepalive-interval 2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_replace_partial_existing(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                peer_link="port1.0.10",
            )]), state="replaced"))
        commands = [
            "mlag domain 10",
            "peer-link port1.0.10",
            "no source-address",
            "no peer-address",
            "no keepalive-interval",
            "no session-timeout",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_replace_partial_new(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=11,
                peer_link="port1.0.10",
            )]), state="replaced"))
        commands = [
            "no mlag domain 10",
            "mlag domain 11",
            "peer-link port1.0.10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_replace_defaults(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                session_timeout="30",
                keepalive_interval="1"
            )]), state="replaced"))
        commands = [
            "mlag domain 10",
            "no source-address",
            "no peer-address",
            "no peer-link",
            "no keepalive-interval",
            "no session-timeout",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_entirely(self):
        set_module_args(dict(config=dict(domains=[]), state="overridden"))
        commands = ["no mlag domain 10"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_all_existing(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
                source_address="1.1.1.2",
                session_timeout="60",
                keepalive_interval="2"
            )]), state="overridden"))
        commands = [
            "mlag domain 10",
            "peer-link port1.0.10",
            "peer-address 1.1.1.1",
            "source-address 1.1.1.2",
            "session-timeout 60",
            "keepalive-interval 2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_all_new(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=11,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
                source_address="1.1.1.2",
                session_timeout="60",
                keepalive_interval="2"
            )]), state="overridden"))
        commands = [
            "no mlag domain 10",
            "mlag domain 11",
            "peer-link port1.0.10",
            "peer-address 1.1.1.1",
            "source-address 1.1.1.2",
            "session-timeout 60",
            "keepalive-interval 2"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_partial_existing(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                peer_link="port1.0.10",
            )]), state="overridden"))
        commands = [
            "mlag domain 10",
            "peer-link port1.0.10",
            "no peer-address",
            "no source-address",
            "no session-timeout",
            "no keepalive-interval"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_partial_new(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=11,
                peer_link="port1.0.10",
            )]), state="overridden"))
        commands = [
            "no mlag domain 10",
            "mlag domain 11",
            "peer-link port1.0.10"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_defaults(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                session_timeout="30",
                keepalive_interval="1"
            )]), state="overridden"))
        commands = [
            "mlag domain 10",
            "no peer-link",
            "no peer-address",
            "no source-address",
            "no session-timeout",
            "no keepalive-interval"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_delete_all(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
                source_address="1.1.1.2",
                session_timeout="60",
                keepalive_interval="2"
            )]), state="deleted"))
        commands = [
            "mlag domain 10",
            "no peer-link",
            "no peer-address",
            "no source-address",
            "no session-timeout",
            "no keepalive-interval"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_delete_partial(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10,
                peer_link="port1.0.10",
                peer_address="1.1.1.1",
            )]), state="deleted"))
        commands = [
            "mlag domain 10",
            "no peer-link",
            "no peer-address"
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_mlag_override_domain(self):
        set_module_args(dict(config=dict(
            domains=[dict(
                domain_id=10
            )]), state="deleted"))
        commands = ["no mlag domain 10"]
        self.execute_module(changed=True, commands=commands)
