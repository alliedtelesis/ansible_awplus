#
# -*- coding: utf-8 -*-
# Copyright 2020 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_lldp_interfaces class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type
from ansible.module_utils.network.common.cfg.base import ConfigBase
from ansible.module_utils.network.common.utils import to_list
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import (
    Facts,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    dict_to_set,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    remove_command_from_config_list,
    add_command_to_config_list,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import (
    filter_dict_having_none_value,
    remove_duplicate_interface,
)


class Lldp_interfaces(ConfigBase):
    """
    The awplus_lldp_interfaces class
    """

    gather_subset = [
        "!all",
        "!min",
    ]

    gather_network_resources = [
        "lldp_interfaces",
    ]

    med_tlv_select_params = {
        "capabilities": "capabilities",
        "inventory_management": "inventory-management",
        "location": "location",
        "network_policy": "network-policy",
        "power_management": "power-management-ext",
    }

    tlv_select_params = {
        "link_aggregation": "link-aggregation",
        "mac_phy_config": "mac-phy-config",
        "management_address": "management-address",
        "max_frame_size": "max-frame-size",
        "port_and_protocol_vlans": "port-and-protocol-vlans",
        "port_description": "port-description",
        "port_vlan": "port-vlan",
        "power_management": "power-management",
        "protocol_ids": "protocol-ids",
        "system_capabilities": "system-capabilities",
        "system_description": "system-description",
        "system_name": "system-name",
        "vlan_names": "vlan-names",
    }

    def __init__(self, module):
        super(Lldp_interfaces, self).__init__(module)

    def get_lldp_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources
        )
        lldp_interfaces_facts = facts["ansible_network_resources"].get(
            "lldp_interfaces"
        )
        if not lldp_interfaces_facts:
            return []
        return lldp_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {"changed": False}
        warnings = list()
        commands = list()

        existing_lldp_interfaces_facts = self.get_lldp_interfaces_facts()
        commands.extend(self.set_config(existing_lldp_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result["changed"] = True
        result["commands"] = commands

        changed_lldp_interfaces_facts = self.get_lldp_interfaces_facts()

        result["before"] = existing_lldp_interfaces_facts
        if result["changed"]:
            result["after"] = changed_lldp_interfaces_facts

        result["warnings"] = warnings
        return result

    def set_config(self, existing_lldp_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params["config"]
        have = existing_lldp_interfaces_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        state = self._module.params["state"]
        if state in ("overridden", "merged", "replaced") and not want:
            self._module.fail_json(
                msg="value of config parameter must not be empty for state {0}".format(
                    state
                )
            )

        if state == "overridden":
            commands = self._state_overridden(want, have)
        elif state == "deleted":
            commands = self._state_deleted(want, have)
        elif state == "merged":
            commands = self._state_merged(want, have)
        elif state == "replaced":
            commands = self._state_replaced(want, have)

        return commands

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for interface in want:
            for each in have:
                if each["name"] == interface["name"]:
                    break
            else:
                continue
            have_dict = filter_dict_having_none_value(interface, each)
            commands.extend(self._clear_config(dict(), have_dict))
            commands.extend(self._set_config(interface, each))
        # Remove the duplicate interface call
        commands = remove_duplicate_interface(commands)

        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for each in have:
            for interface in want:
                if each["name"] == interface["name"]:
                    break
            else:
                # We didn't find a matching desired state, which means we can
                # pretend we recieved an empty desired state.
                interface = dict(name=each["name"])
                commands.extend(self._clear_config(interface, each))
                continue
            have_dict = filter_dict_having_none_value(interface, each)
            commands.extend(self._clear_config(dict(), have_dict))
            commands.extend(self._set_config(interface, each))
        # Remove the duplicate interface call
        commands = remove_duplicate_interface(commands)
        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []

        for interface in want:
            for each in have:
                if interface["name"] == each["name"]:
                    break
            else:
                continue
            commands.extend(self._set_config(interface, each))

        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []

        if want:
            for interface in want:
                for each in have:
                    if each["name"] == interface["name"]:
                        break
                else:
                    continue
                interface = dict(name=interface["name"])
                commands.extend(self._clear_config(interface, each))
        else:
            for each in have:
                commands.extend(self._clear_config(dict(), each))

        return commands

    def _set_config(self, want, have):
        # Set the interface config based on the want and have config
        commands = []

        interface = "interface " + have["name"]
        # Get the diff b/w want and have
        want_dict = dict_to_set(want)
        have_dict = dict_to_set(have)
        diff = want_dict - have_dict

        if diff:
            diff = dict(diff)
            receive = diff.get("receive")
            transmit = diff.get("transmit")
            med_tlv_select = diff.get("med_tlv_select")
            tlv_select = diff.get("tlv_select")
            if receive:
                cmd = "lldp receive"
                add_command_to_config_list(interface, cmd, commands)
            elif receive is False:
                cmd = "no lldp receive"
                add_command_to_config_list(interface, cmd, commands)
            if transmit:
                cmd = "lldp transmit"
                add_command_to_config_list(interface, cmd, commands)
            elif transmit is False:
                cmd = "no lldp transmit"
                add_command_to_config_list(interface, cmd, commands)

            if med_tlv_select:
                med_tlv_select = dict(med_tlv_select)
                for option, isenabled in med_tlv_select.items():
                    if isenabled:
                        add_command_to_config_list(
                            interface,
                            "lldp med-tlv-select {0}".format(
                                self.med_tlv_select_params.get(option)
                            ),
                            commands,
                        )
                    # else:
                    #     add_command_to_config_list(interface, 'no lldp med-tlv-select {0}'.format(self.med_tlv_select_params.get(option)), commands)
            if tlv_select:
                tlv_select = dict(tlv_select)
                for option, isenabled in tlv_select.items():
                    if isenabled:
                        add_command_to_config_list(
                            interface,
                            "lldp tlv-select {0}".format(
                                self.tlv_select_params.get(option)
                            ),
                            commands,
                        )
                    # else:
                    #     add_command_to_config_list(interface, 'no lldp tlv-select {0}'.format(self.tlv_select_params.get(option)), commands)

        return commands

    def _clear_config(self, want, have):
        # Delete the interface config based on the want and have config
        commands = []
        if want.get("name"):
            interface = "interface " + want["name"]
        else:
            interface = "interface " + have["name"]

        if have.get("receive") and have.get("receive") != want.get("receive"):
            cmd = "lldp receive"
            remove_command_from_config_list(interface, cmd, commands)
        if have.get("transmit") and have.get("transmit") != want.get("transmit"):
            cmd = "lldp transmit"
            remove_command_from_config_list(interface, cmd, commands)

        return commands
