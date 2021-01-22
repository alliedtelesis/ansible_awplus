#
# (c) 2019, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import (
    awplus_lldp_interfaces,
)
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusLldpGlobalModule(TestAwplusModule):
    module = awplus_lldp_interfaces

    def setUp(self):
        super(TestAwplusLldpGlobalModule, self).setUp()

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

        self.mock_execute_show_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.lldp_interfaces.lldp_interfaces."
            "Lldp_interfacesFacts.get_device_data"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

        self.mock_execute_show_int_command = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.lldp_interfaces.lldp_interfaces."
            "Lldp_interfacesFacts.get_int_brief"
        )
        self.execute_show_int_command = self.mock_execute_show_int_command.start()

    def tearDown(self):
        super(TestAwplusLldpGlobalModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        def load_from_file(*args, **kwargs):
            return load_fixture("awplus_lldp_interfaces.cfg")

        self.execute_show_command.side_effect = load_from_file
        self.execute_show_int_command.return_value = ["port1.0.1", "port1.0.2", "port1.0.3", "port1.0.4"]

    def test_awplus_lldp_interfaces_merged(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="port1.0.2",
                        receive=True,
                        med_tlv_select=dict(network_policy=False),
                        tlv_select=dict(protocol_ids=True),
                    )
                ],
                state="merged",
            )
        )
        commands = [
            "interface port1.0.2",
            "lldp receive",
            "lldp tlv-select protocol-ids",
            "no lldp med-tlv-select network-policy",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lldp_interfaces_merged_idempotent(self):
        set_module_args(
            dict(
                config=[dict(name="port1.0.2", receive=False, transmit=False)],
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_lldp_interfaces_replaced(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="port1.0.3",
                        transmit=False,
                        receive=True,
                        med_tlv_select=dict(network_policy=False),
                        tlv_select=dict(protocol_ids=True),
                    )
                ],
                state="replaced",
            )
        )
        commands = [
            "interface port1.0.3",
            "no lldp transmit",
            "lldp receive",
            "no lldp med-tlv-select network-policy",
            "lldp tlv-select protocol-ids",
            "no lldp tlv-select link-aggregation",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lldp_interfaces_replaced_idempotent(self):
        set_module_args(
            dict(
                config=[dict(name="port1.0.3", receive=False, tlv_select=dict(link_aggregation=True))],
                state="replaced",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_lldp_interfaces_overridden(self):
        set_module_args(
            dict(
                config=[
                    dict(name="port1.0.1", transmit=True, receive=True),
                    dict(name="port1.0.2", transmit=False, receive=False),
                    dict(name="port1.0.3"),
                    dict(
                        name="port1.0.4",
                        transmit=False,
                        med_tlv_select=dict(network_policy=True),
                        tlv_select=dict(protocol_ids=True),
                    ),
                ],
                state="overridden",
            )
        )
        commands = [
            "interface port1.0.2",
            "no lldp med-tlv-select inventory-management",
            "lldp med-tlv-select location",
            "no lldp tlv-select link-aggregation",
            "no lldp tlv-select mac-phy-config",
            "no lldp tlv-select management-address",
            "interface port1.0.3",
            "lldp receive",
            "no lldp tlv-select link-aggregation",
            "interface port1.0.4",
            "no lldp transmit",
            "lldp tlv-select protocol-ids",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_lldp_interfaces_overridden_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="port1.0.2",
                        receive=False,
                        transmit=False,
                        med_tlv_select=dict(inventory_management=True, location=False),
                        tlv_select=dict(management_address=True, mac_phy_config=True, link_aggregation=True),
                    ),
                    dict(name="port1.0.3", receive=False, tlv_select=dict(link_aggregation=True)),
                ],
                state="overridden",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_awplus_lldp_interfaces_deleted(self):
        set_module_args(dict(config=[dict(name="port1.0.3")], state="deleted"))
        commands = [
            "interface port1.0.3",
            "lldp receive",
            "no lldp tlv-select link-aggregation",
        ]
        self.execute_module(changed=True, commands=commands)
