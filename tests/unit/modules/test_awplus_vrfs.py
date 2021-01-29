#
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
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_vrfs
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusVrfsModule(TestAwplusModule):
    module = awplus_vrfs

    def setUp(self):
        super(TestAwplusVrfsModule, self).setUp()

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

        self.mock_get_data = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.vrfs.vrfs.VrfsFacts.get_data"
        )
        self.get_data = self.mock_get_data.start()

    def tearDown(self):
        super(TestAwplusVrfsModule, self).tearDown()

        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_data.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        self.get_data.return_value = load_fixture("awplus_vrf_config.cfg")

    def test_awplus_vrf_name(self):
        ''' Create a new VRF.
        '''
        set_module_args(
            dict(
                config=[{"name": "test_4", "id": "3"}],
                state="merged",
            )
        )
        commands = ["ip vrf test_4 3"]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_awplus_vrf_name_unchanged(self):
        ''' Merge operation on a particular VRF with no changes.
        '''
        set_module_args(
            dict(
                config=[{"name": "test_1", "id": "2"}],
                state="merged",
            )
        )
        self.execute_module(changed=False)

    def test_awplus_vrf_description(self):
        ''' Change the description with a merge.
        '''
        set_module_args(
            dict(
                config=[{"name": "test_1", "id": "2", "description": "test string"}],
                state="merged",
            )
        )
        commands = ["ip vrf test_1 2", " description test string"]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_awplus_vrf_new_rd(self):
        ''' Specify an rd when one wasn't there before.
        '''
        set_module_args(
            dict(
                config=[{"name": "test_1", "id": "2", "rd": "2:100"}],
                state="merged",
            )
        )
        commands = ["ip vrf test_1 2", " rd 2:100"]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_awplus_vrf_delete(self):
        ''' Delete a VRF.
        '''
        set_module_args(
            dict(
                config=[{"name": "test_1", "id": "2"}],
                state="deleted"
            )
        )
        commands = ["no ip vrf test_1"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vrf_purge_all(self):
        ''' Remove all VRFs with an override.
        '''
        set_module_args(
            dict(
                config=[],
                state="overridden",
            )
        )
        commands = ["no ip vrf test_1", "no ip vrf red"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_vrfs_no_purge(self):
        ''' Merge on both VRFs with no parameters.
        '''
        set_module_args(
            dict(
                config=[{"name": "test_1", "id": "2"}, {"name": "red", "id": "1"}],
                state="merged",
            )
        )
        commands = []
        self.execute_module(changed=False, commands=commands)
