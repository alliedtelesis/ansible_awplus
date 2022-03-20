from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.alliedtelesis.awplus.tests.unit.compat.mock import patch
from ansible_collections.alliedtelesis.awplus.plugins.modules import awplus_openflow
from ansible_collections.alliedtelesis.awplus.tests.unit.utils import set_module_args
from .awplus_module import TestAwplusModule, load_fixture


class TestAwplusOpenFlowModule(TestAwplusModule):
    module = awplus_openflow

    def setUp(self):
        super(TestAwplusOpenFlowModule, self).setUp()

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

        self.mock_get_openflow_conf = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.openflow.openflow.OpenflowFacts.get_openflow_conf"
        )
        self.get_openflow_conf = (
            self.mock_get_openflow_conf.start()
        )

        self.mock_get_openflow_stat = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.openflow.openflow.OpenflowFacts.get_openflow_stat"
        )
        self.get_openflow_stat = (
            self.mock_get_openflow_stat.start()
        )

        self.mock_get_run_openflow = patch(
            "ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.openflow.openflow.OpenflowFacts.get_run_openflow"
        )
        self.get_run_openflow = (
            self.mock_get_run_openflow.start()
        )

    def tearDown(self):
        super(TestAwplusOpenFlowModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_get_openflow_conf.stop()
        self.mock_get_openflow_stat.stop()
        self.mock_get_run_openflow.stop()

    def load_fixtures(self, commands=None, transport="cli"):
        self.get_openflow_conf.return_value = load_fixture("awplus_openflow_config.cfg").splitlines()
        self.get_openflow_stat.return_value = []
        self.get_run_openflow.return_value = load_fixture("awplus_openflow_show_run.cfg").splitlines()

    def test_awplus_openflow_add_existing_controller(self):
        set_module_args(
            dict(
                config=dict(
                    controllers=[
                        dict(
                            name="test_ssl1",
                            protocol="ssl",
                            address="192.56.8.3",
                            l4_port=8,
                        )
                    ],
                ),
                state="merged",
            )
        )
        commands = ["no openflow controller test_ssl1", "openflow controller test_ssl1 ssl 192.56.8.3 8"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_add_new_controller(self):
        set_module_args(
            dict(config=dict(controllers=[dict(name="oc2", protocol="tcp", address="184.5.3.2", l4_port=10)]), state="merged")
        )
        commands = ["openflow controller oc2 tcp 184.5.3.2 10"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_remove_existing_controller(self):
        set_module_args(
            dict(
                config=dict(
                    controllers=[
                        dict(
                            name="test_ssl1",
                            protocol="ssl",
                            address="192.56.8.3",
                            l4_port=8,
                        )
                    ],
                ),
                state="deleted",
            )
        )
        commands = ["no openflow controller test_ssl1"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_remove_nonexisitng_controller(self):
        set_module_args(
            dict(
                config=dict(
                    controllers=[
                        dict(name="oc2", protocol="ssl", address="192.56.8.3", l4_port=8)
                    ],
                ),
                state="deleted",
            )
        )
        self.execute_module(failed=True, changed=False)

    def test_awplus_openflow_add_existing_port(self):
        set_module_args(dict(config=dict(ports=["port1.0.1"]), state="merged"))
        self.execute_module(changed=False)

    def test_awplus_openflow_add_new_port(self):
        set_module_args(dict(config=dict(ports=["port1.0.2"]), state="merged"))
        commands = ["interface port1.0.2", "openflow"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_remove_existing_port(self):
        set_module_args(dict(config=dict(ports=["port1.0.1"]), state="deleted"))
        commands = ["interface port1.0.1", "no openflow"]
        result = self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_remove_nonexisting_port(self):
        set_module_args(dict(config=dict(ports=["port1.0.2"]), state="deleted"))
        self.execute_module(changed=False)

    def test_awplus_openflow_modify_native_vlan(self):
        set_module_args(dict(config=dict(native_vlan=3), state="merged"))
        commands = ["openflow native vlan 3"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_default_native_vlan(self):
        set_module_args(dict(config=dict(native_vlan=2), state="deleted"))
        commands = ["no openflow native vlan"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_modify_fail_mode(self):
        set_module_args(dict(config=dict(fail_mode="secure_nre"), state="merged"))
        commands = ["openflow failmode secure non-rule-expired"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_default_fail_mode(self):
        set_module_args(dict(config=dict(fail_mode="standalone"), state="deleted"))
        commands = ["no openflow failmode"]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_remove_all_config(self):
        set_module_args(dict(config=dict(controllers=[], ports=[]), state="overridden"))
        commands = [
            "no openflow controller test_ssl1",
            "no openflow controller oc1",
            "no openflow controller test_ssl",
            "no openflow controller controller1",
            "no openflow datapath-id",
            "interface port1.0.1",
            "no openflow",
            "no openflow native vlan",
            "no openflow failmode",
            "no openflow inactivity",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_awplus_openflow_invalid_port_name(self):
        set_module_args(dict(config=dict(ports=["vlan1"], state="merged")))
        self.execute_module(changed=False, failed=True)
