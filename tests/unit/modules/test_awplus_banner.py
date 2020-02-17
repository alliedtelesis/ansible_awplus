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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_banner
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusBannerModule(TestAwplusModule):

    module = awplus_banner

    def setUp(self):
        super(TestAwplusBannerModule, self).setUp()

        self.mock_get_config = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.modules.awplus_banner.get_config"
        )
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.modules.awplus_banner.load_config"
        )
        self.load_config = self.mock_load_config.start()

    def tearDown(self):
        super(TestAwplusBannerModule, self).tearDown()
        self.mock_get_config.stop()
        self.mock_load_config.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_banner_show_running_config_awplus.txt")

        self.get_config.side_effect = load_from_file

    def test_awplus_banner_create(self):
        for banner_type in ("motd", "exec"):
            set_module_args(dict(banner=banner_type, text="test\nbanner\nstring"))
            commands = ["banner {0} test\nbanner\nstring".format(banner_type)]
            self.execute_module(changed=True, commands=commands)

    def test_awplus_banner_remove(self):
        set_module_args(dict(banner="exec", state="absent"))
        commands = ["no banner exec"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_banner_nochange(self):
        banner_text = load_fixture("awplus_banner_show_banner.txt")
        set_module_args(dict(banner="exec", text=banner_text))
        self.execute_module()
