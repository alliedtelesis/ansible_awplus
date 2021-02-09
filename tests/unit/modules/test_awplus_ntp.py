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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_ntp
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusNtpModule(TestAwplusModule):

    module = awplus_ntp

    def setUp(self):
        super(TestAwplusNtpModule, self).setUp()

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

        self.mock_get_data = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.ntp.ntp.NtpFacts.get_run_conf"
        )
        self.get_data = self.mock_get_data.start()

    def tearDown(self):
        super(TestAwplusNtpModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_data.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        self.get_data.return_value = load_fixture("awplus_ntp_config.cfg")

    def test_awplus_ntp_idempotent(self):
        set_module_args(
            dict(
                config=dict(
                    server=["10.75.33.5"],
                    authentication=[dict(key_id=8900, key_type="md5", auth_key="fdasgf")],
                    source_int="192.66.44.33"
                )
            )
        )
        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_awplus_ntp_merge(self):
        set_module_args(
            dict(
                config=dict(
                    server=["10.75.33.6"],
                    authentication=[dict(key_id=1, key_type="md5", auth_key="ackrmn")],
                )
            )
        )
        commands = ["ntp server 10.75.33.6", "ntp authentication-key 1 md5 ackrmn"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_ntp_replace(self):
        set_module_args(
            dict(
                config=dict(
                    authentication=[dict(key_id=104, key_type="md5", auth_key="jaegr")],),
                state="replaced",
            )
        )
        commands = ["no ntp authentication-key 8900", "ntp authentication-key 104 md5 jaegr"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_ntp_replace_server(self):
        set_module_args(
            dict(
                config=dict(
                    server=["10.75.33.7"],),
                state="replaced",
            )
        )
        commands = ["no ntp server 10.75.33.5", "ntp server 10.75.33.7"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_replace_idempotent(self):
        set_module_args(
            dict(
                config=dict(authentication=[dict(key_id=8900, key_type="md5", auth_key="fdasgf")],),
                state="replaced",
            )
        )
        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_awplus_ntp_overridden(self):
        set_module_args(
            dict(
                config=dict(
                    authentication=[dict(key_id=104, key_type="md5", auth_key="jaegr")],),
                state="overridden",
            )
        )
        commands = ["no ntp server 10.75.33.5", "no ntp source", "no ntp authentication-key 8900", "ntp authentication-key 104 md5 jaegr"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_overridden_idempotent(self):
        set_module_args(
            dict(
                config=dict(
                    server=["10.75.33.5"],
                    authentication=[dict(key_id=8900, key_type="md5", auth_key="fdasgf")],
                    source_int="192.66.44.33"
                ),
                state="overridden",
            )
        )
        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_awplus_ntp_deleted(self):
        set_module_args(
            dict(
                config=dict(
                    authentication=[dict(key_id=8900, key_type="md5", auth_key="fdasgf")],),
                state="deleted",
            )
        )
        commands = ["no ntp authentication-key 8900"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_deleted_all(self):
        set_module_args(
            dict(
                state="deleted",
            )
        )
        commands = ["no ntp server 10.75.33.5", "no ntp source", "no ntp authentication-key 8900"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_ntp_deleted_none(self):
        set_module_args(
            dict(
                config=dict(
                    authentication=[dict(key_id=104, key_type="md5", auth_key="fdasgf")],),
                state="deleted",
            )
        )
        commands = []
        self.execute_module(changed=False, commands=commands)
