#
# (c) 2020 Allied Telesis
# (c) 2017 Paul Neumann
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

import json

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_logging
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusLoggingModule(TestAwplusModule):

    module = awplus_logging

    def setUp(self):
        super(TestAwplusLoggingModule, self).setUp()

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
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.logging.logging.LoggingFacts.get_run_conf"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestAwplusLoggingModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_logging_config.cfg")

        self.execute_show_command.side_effect = load_from_file

    def test_awplus_logging_merged(self):
        set_module_args(dict(config=[dict(dest="console", facility="cron")], state="merged"))
        commands = ["log console facility cron"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_logging_merged_idempotent(self):
        set_module_args(dict(config=[dict(dest="buffered", size=51)], state="merged"))
        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_awplus_logging_deleted(self):
        set_module_args(dict(config=[dict(dest="buffered", size=51)], state="deleted"))
        commands = ["no log buffered size"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_logging_deleted_all(self):
        set_module_args(dict(state="deleted"))
        commands = ["no log buffered size",
                    "no log console level alerts facility ftp",
                    "no log host f"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_logging_replaced(self):
        set_module_args(dict(config=[dict(dest="console", facility="cron")], state="replaced"))
        commands = ["log console facility cron",
                    "no log console level alerts facility ftp"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_logging_replaced_idempotent(self):
        set_module_args(dict(config=[dict(dest="console", level="alerts", facility="ftp")], state="replaced"))
        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_awplus_logging_overridden(self):
        set_module_args(dict(config=[dict(dest="console", facility="cron")], state="overridden"))
        commands = ["log console facility cron",
                    "no log buffered size",
                    "no log console level alerts facility ftp",
                    "no log host f"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_logging_overridden_idempotent(self):
        set_module_args(dict(config=[dict(dest="console", level="alerts", facility="ftp"),
                                     dict(dest="buffered", size=51),
                                     dict(dest="host", name="f", level="warnings")], state="overridden"))
        commands = []
        self.execute_module(changed=False, commands=commands)
