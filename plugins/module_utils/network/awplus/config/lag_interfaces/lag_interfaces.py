#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_lag_interfaces class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base import (
    ConfigBase,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts


class Lag_interfaces(ConfigBase):
    """
    The awplus_lag_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'lag_interfaces',
    ]

    def __init__(self, module):
        super(Lag_interfaces, self).__init__(module)

    def get_lag_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        lag_interfaces_facts = facts['ansible_network_resources'].get('lag_interfaces')
        if not lag_interfaces_facts:
            return []
        return lag_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_lag_interfaces_facts = self.get_lag_interfaces_facts()
        commands.extend(self.set_config(existing_lag_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_lag_interfaces_facts = self.get_lag_interfaces_facts()

        result['before'] = existing_lag_interfaces_facts
        if result['changed']:
            result['after'] = changed_lag_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_lag_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_lag_interfaces_facts
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
        state = self._module.params['state']
        if state == 'overridden':
            commands = self._state_overridden(have, want)
        elif state == 'deleted':
            commands = self._state_deleted(have, want)
        elif state == 'merged':
            commands = self._state_merged(have, want)
        elif state == 'replaced':
            commands = self._state_replaced(have, want)
        return commands

    def _state_replaced(self, have, want):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        by_member, want_groups, have_groups = self.conf_by_member(have, want)
        if by_member is None:
            return []

        return self.gen_commands(by_member, want_groups)

    def _state_overridden(self, have, want):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        by_member, want_groups, have_groups = self.conf_by_member(have, want)
        if by_member is None:
            return []

        return self.gen_commands(by_member, have_groups + want_groups)

    def _state_merged(self, have, want):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        by_member, want_groups, have_groups = self.conf_by_member(have, want)
        if by_member is None:
            return []

        return self.gen_commands(by_member, want_groups, merge=True)

    def _state_deleted(self, have, want):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        by_member, want_groups, have_groups = self.conf_by_member(have, want)
        if by_member is None:
            return []

        return self.gen_commands(by_member, want_groups, delete=True)

    def conf_by_member(self, have, want):
        """ Return a dictionary of have and want indexed by member port. This
        can be used to generate required commands more easily.
        :rtype: dict
        :returns: have/want expressed by member port. May return None if
                  errors found (caller can fail)
        """
        ret_member = {}
        ret_want_group = []
        ret_have_group = []
        for group in have:
            ret_have_group.append(group.get("name"))
            for member in group.get("members"):
                port = member.get("member")
                if port in ret_member and ret_member[port].get["have"]:
                    self._module.fail_json(msg="duplicate port in current config")
                    return None, None, None
                ret_member[port] = {"have": {"group": group.get("name"), "mode": member.get("mode")}}
        for group in want:
            ret_want_group.append(group.get("name"))
            if group.get("members"):
                for member in group.get("members"):
                    port = member.get("member")
                    if port not in ret_member:
                        ret_member[port] = {"want": {"group": group.get("name"), "mode": member.get("mode")}}
                    else:
                        if "want" in ret_member[port]:
                            self._module.fail_json(msg="duplicate port in desired config")
                            return None, None, None
                        ret_member[port].update({"want": {"group": group.get("name"), "mode": member.get("mode")}})
        return ret_member, ret_want_group, ret_have_group

    def gen_commands(self, by_member, want_groups, merge=False, delete=False):
        """ Generate commands for interfaces, for groups in the list.
        :param: by_member: dictionary of have/want by member port.
        :param: want_groups: list of groups for which to apply config
        :param: merge: is this a replace/override or merge?
        :param: delete: is this a delete?
        :rtype: list
        :returns: List of commands required to get to desired result
        """
        cmds = []
        for port_name in by_member:
            port_actions = by_member.get(port_name)
            h = port_actions.get("have")
            w = port_actions.get("want")
            h_group = h.get("group") if h else None
            w_group = w.get("group") if w else None
            h_mode = h.get("mode") if h else None
            w_mode = w.get("mode") if w else None
            changed = h_group != w_group or h_mode != w_mode
            if not delete:
                if w_group in want_groups or (w is None and h_group in want_groups):
                    if changed:
                        cmds.append("interface {}".format(port_name))
                        if h and ((not w and not merge) or (w and h_group != w_group)):
                            cmds.append("no channel-group")
                        if w and (not h or h_mode != w_mode or h_group != w_group):
                            cmds.append("channel-group {} mode {}".format(w_group, w_mode))
            elif h_group == w_group and w_group in want_groups:
                cmds.append("interface {}".format(port_name))
                cmds.append("no channel-group")
        return cmds
