#
# -*- coding: utf-8 -*-
# Copyright 2020 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The awplus_interfaces class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""
import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base import ConfigBase
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.facts.facts import (
    Facts,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.utils.utils import (
    get_interface_type,
    dict_to_set,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.utils.utils import (
    remove_command_from_config_list,
    add_command_to_config_list,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.utils.utils import (
    filter_dict_having_none_value,
    remove_duplicate_interface,
)
from copy import deepcopy


class Interfaces(ConfigBase):
    """
    The awplus_interfaces class
    """

    gather_subset = [
        "!all",
        "!min",
    ]

    gather_network_resources = [
        "interfaces",
    ]

    params = ("description", "mtu", "speed", "duplex")

    def __init__(self, module):
        super(Interfaces, self).__init__(module)

    def get_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources
        )
        interfaces_facts = facts["ansible_network_resources"].get("interfaces")
        if not interfaces_facts:
            return []
        return interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {"changed": False}
        warnings = list()
        commands = list()

        existing_interfaces_facts = self.get_interfaces_facts()
        commands.extend(self.set_config(existing_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                warning = self._connection.edit_config(commands).get("response")
                for warn in warning:
                    if warn != "":
                        warnings.append(warn)
            result["changed"] = True
        result["commands"] = commands

        changed_interfaces_facts = self.get_interfaces_facts()

        result["before"] = existing_interfaces_facts
        if result["changed"]:
            result["after"] = changed_interfaces_facts

        result["warnings"] = warnings
        return result

    def set_config(self, existing_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params["config"]
        have = existing_interfaces_facts
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

    def get_interfaces(self, want):
        """ Validates input and returns a list of interfaces to configure

        :param want: the name of the interface/s
        :rtype: list
        :returns: list of interfaces to configure
        """
        if " " in want:
            self._module.fail_json("Interface names and comma-separated names should not have spaces.")
        if "," in want:
            intfs = want.split(",")
            int_type = get_interface_type(intfs[0])
            for intf in intfs:
                intf_type = get_interface_type(intf)
                if intf_type == "unknown":
                    self._module.fail_json("Invalid interface - unknown interface")
                if int_type != intf_type:
                    self._module.fail_json("Interfaces mismatch, Interfaces in range must be of the same type")
            return intfs
        else:
            return [want]

    def get_port_dict(self, want, have):
        """ Determines whether the given port/s exist and returns the configuration of the wanted port,
            blank dict for range and none if the port does not exist
        :param want: the name of the port
        :param have: the current configuration as a dictionary
        :rtype: dict
        :returns: configuration of the wanted port
        """
        start = want
        end = want
        if "-" in want:
            port = re.search(r"port(\d+).(\d+).(\d+)-(\d+).(\d+).(\d+)", want)
            if port:
                for i in range(3):  # check if valid range
                    if int(port.group(i + 1)) > int(port.group(i + 4)):
                        self._module.fail_json("Invalid Input - range end must be greater than range start")
                    elif int(port.group(i + 1)) == int(port.group(i + 4)):
                        continue
                    else:
                        break
                else:
                    self._module.fail_json("Invalid Input - range end must be greater than range start")
                start = "port{}.{}.{}".format(port.group(1), port.group(2), port.group(3))
                end = "port{}.{}.{}".format(port.group(4), port.group(5), port.group(6))
        start_exists = False
        end_exists = False
        for intf in have:  # check if port exists
            if start == intf["name"]:
                start_exists = True
            if end == intf["name"]:
                end_exists = True
            if start == end and start_exists:
                return intf
        if start_exists and end_exists:
            return dict()
        return

    def get_have_dict(self, want, have):
        """ Determines whether the given interface/s exist and returns the configuration of the wanted interface,
            blank dict for range and none if the interface does not exist
        :param want: the name of the interface
        :param have: the current configuration as a dictionary
        :rtype: dict
        :returns: configuration of the wanted interface
        """
        if want.startswith("port"):
            return self.get_port_dict(want, have)
        if "-" in want:
            intf_range = re.search(r"([a-z]+)(\d+)-(\d+)", want)
            if intf_range:
                if int(intf_range.group(3)) <= int(intf_range.group(2)):
                    self._module.fail_json("Invalid Input - range end must be greater than range start")
                for i in range(int(intf_range.group(2)), int(intf_range.group(3)) + 1):
                    for intf in have:  # check if all interfaces in range exists
                        if intf_range.group(1) + str(i) == intf["name"]:
                            break
                    else:
                        return  # returns none if one of the interfaces does not exist
                return dict()
        else:
            for intf in have:  # check for singular input
                if want == intf["name"]:
                    return intf
            return

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced
        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the deisred configuration
        """
        commands = []

        for interface in want:
            intfs = self.get_interfaces(interface["name"])
            for intf in intfs:
                have_dict = self.get_have_dict(intf, have)
                if have_dict is None:
                    self._module.fail_json(msg="Interface does not exist")
                if have_dict:
                    partial_want = deepcopy(interface)
                    partial_want["name"] = intf
                    filtered_have = filter_dict_having_none_value(partial_want, have_dict)
                    commands.extend(self._clear_config(dict(), filtered_have))
                    commands.extend(self._set_config(partial_want, have_dict))
                else:
                    commands.extend(self._set_config(interface, dict()))
        # Remove the duplicate interface call
        commands = remove_duplicate_interface(commands)

        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden
        :param want: the desired configuration as a dictionary
        :param obj_in_have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for each in have:
            for interface in want:
                count = 0
                if each["name"] == interface["name"]:
                    break
                count += 1
            else:
                # We didn't find a matching desired state, which means we can
                # pretend we recieved an empty desired state.
                interface = dict(name=each["name"])
                commands.extend(self._clear_config(interface, each))
                continue
            have_dict = filter_dict_having_none_value(interface, each)
            commands.extend(self._clear_config(dict(), have_dict))
            commands.extend(self._set_config(interface, each))
            # as the pre-existing interface are now configured by
            # above set_config call, deleting the respective
            # interface entry from the want list
            del want[count]

        # Iterating through want list which now only have range interfaces to be
        # configured
        for interface in want:
            intfs = self.get_interfaces(interface["name"])
            for intf in intfs:
                have_dict = self.get_have_dict(intf, have)
                if have_dict is None:
                    self._module.fail_json(msg="Interface does not exist")
                if have_dict:
                    partial_want = deepcopy(interface)
                    partial_want["name"] = intf
                    commands.extend(self._set_config(partial_want, have_dict))
                else:
                    commands.extend(self._set_config(interface, dict()))
        # Remove the duplicate interface call
        commands = remove_duplicate_interface(commands)

        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged
        :param want: the additive configuration as a dictionary
        :param obj_in_have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []

        for interface in want:
            intfs = self.get_interfaces(interface["name"])
            for intf in intfs:
                have_dict = self.get_have_dict(intf, have)
                if have_dict is None:
                    self._module.fail_json(msg="Interface does not exist")
                if have_dict:
                    partial_want = deepcopy(interface)
                    partial_want["name"] = intf
                    commands.extend(self._set_config(partial_want, have_dict))
                else:
                    commands.extend(self._set_config(interface, dict()))
            # commands.extend(self._clear_config(dict(), have_dict))

        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted
        :param want: the objects from which the configuration should be removed
        :param obj_in_have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []

        if want:
            for interface in want:
                intfs = self.get_interfaces(interface["name"])
                for intf in intfs:
                    have_dict = self.get_have_dict(intf, have)
                    if have_dict is None:
                        self._module.fail_json(msg="Interface does not exist")
                else:
                    if have_dict:
                        interface = dict(name=interface["name"])
                        commands.extend(self._clear_config(interface, have_dict))
        else:
            for each in have:
                commands.extend(self._clear_config(dict(), each))

        return commands

    def _set_config(self, want, have):
        # Set the interface config based on the want and have config
        commands = []
        interface = "interface " + want["name"]

        # Get the diff b/w want and have
        want_dict = dict_to_set(want)
        have_dict = dict_to_set(have)
        diff = want_dict - have_dict
        # raise ValueError(have_dict)
        if diff:
            diff = dict(diff)
            for item in self.params:
                if diff.get(item):
                    cmd = item + " " + str(want.get(item))
                    add_command_to_config_list(interface, cmd, commands)
            if diff.get("enabled"):
                add_command_to_config_list(interface, "no shutdown", commands)
            elif diff.get("enabled") is False:
                add_command_to_config_list(interface, "shutdown", commands)

        return commands

    def _clear_config(self, want, have):
        # Delete the interface config based on the want and have config
        commands = []

        if want.get("name"):
            interface = "interface " + want["name"]
        else:
            interface = "interface " + have["name"]

        if have.get("description") and want.get("description") != have.get(
            "description"
        ):
            remove_command_from_config_list(interface, "description", commands)
        if not have.get("enabled") and want.get("enabled") != have.get("enabled"):
            # if enable is False set enable as True which is the default behavior
            remove_command_from_config_list(interface, "shutdown", commands)
        if have.get("mtu") and want.get("mtu") != have.get("mtu"):
            remove_command_from_config_list(interface, "mtu", commands)
        if (
            have.get("speed")
            and have.get("speed") != "auto"
            and want.get("speed") != have.get("speed")
        ):
            remove_command_from_config_list(interface, "speed", commands)
        if (
            have.get("duplex")
            and have.get("duplex") != "auto"
            and want.get("duplex") != have.get("duplex")
        ):
            remove_command_from_config_list(interface, "duplex", commands)

        return commands
