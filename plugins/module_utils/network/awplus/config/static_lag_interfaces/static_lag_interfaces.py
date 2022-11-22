#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_static_lag_interfaces class
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


class Static_lag_interfaces(ConfigBase):
    """
    The awplus_static_lag_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'static_lag_interfaces',
    ]

    def __init__(self, module):
        super(Static_lag_interfaces, self).__init__(module)

    def get_static_lag_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        static_lag_interfaces_facts = facts['ansible_network_resources'].get('static_lag_interfaces')
        if not static_lag_interfaces_facts:
            return {}
        return static_lag_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_static_lag_interfaces_facts = self.get_static_lag_interfaces_facts()
        commands.extend(self.set_config(existing_static_lag_interfaces_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_static_lag_interfaces_facts = self.get_static_lag_interfaces_facts()

        result['before'] = existing_static_lag_interfaces_facts
        if result['changed']:
            result['after'] = changed_static_lag_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_static_lag_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_static_lag_interfaces_facts
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
        commands = []
        h_b_p, w_b_p, h_g, w_g = self.gen_action_lists(have, want)
        ports_cleared, commands = self.gen_commands_phase_1(h_b_p, w_b_p, h_g, w_g)
        for g in w_g:
            redo = g in h_g and h_g[g] != w_g[g]
            for port in w_b_p:
                if w_b_p[port] == g:
                    new_port = port not in h_b_p
                    change_port = port in h_b_p and (h_b_p[port] != w_b_p[port] or redo)
                    if new_port or change_port:
                        commands.append(f"interface {port}")
                        if change_port and port not in ports_cleared:
                            commands.append("no static-channel-group")
                            ports_cleared.append(port)
                        if w_g[g]:
                            commands.append(f"static-channel-group {g} member-filters")
                        else:
                            commands.append(f"static-channel-group {g}")
            for port in h_b_p:
                if h_b_p[port] == g:
                    if port not in w_b_p or (port in w_b_p and h_b_p[port] != w_b_p[port]):
                        if port not in ports_cleared:
                            commands.append(f"interface {port}")
                            commands.append("no static-channel-group")
                            ports_cleared.append(port)
        return commands

    def _state_overridden(self, have, want):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        h_b_p, w_b_p, h_g, w_g = self.gen_action_lists(have, want)
        ports_cleared, commands = self.gen_commands_phase_1(h_b_p, w_b_p, h_g, w_g)
        for g in w_g:
            redo = g in h_g and h_g[g] != w_g[g]
            for port in w_b_p:
                if w_b_p[port] == g:
                    new_port = port not in h_b_p
                    change_port = port in h_b_p and (h_b_p[port] != w_b_p[port] or redo)
                    if new_port or change_port:
                        commands.append(f"interface {port}")
                        if change_port and port not in ports_cleared:
                            commands.append("no static-channel-group")
                            ports_cleared.append(port)
                        if w_g[g]:
                            commands.append(f"static-channel-group {g} member-filters")
                        else:
                            commands.append(f"static-channel-group {g}")
            for port in h_b_p:
                if h_b_p[port] == g:
                    if port not in w_b_p or (port in w_b_p and h_b_p[port] != w_b_p[port]):
                        if port not in ports_cleared:
                            commands.append(f"interface {port}")
                            commands.append("no static-channel-group")
                            ports_cleared.append(port)
        for g in h_g:
            if g not in w_g:
                for port in h_b_p:
                    if h_b_p[port] == g and port not in w_b_p:
                        if port not in ports_cleared:
                            commands.append(f"interface {port}")
                            commands.append("no static-channel-group")
                            ports_cleared.append(port)
        return commands

    def _state_merged(self, have, want):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        h_b_p, w_b_p, h_g, w_g = self.gen_action_lists(have, want)
        ports_cleared, commands = self.gen_commands_phase_1(h_b_p, w_b_p, h_g, w_g)
        for g in w_g:
            redo = g in h_g and h_g[g] != w_g[g]
            for port in w_b_p:
                if w_b_p[port] == g:
                    new_port = port not in h_b_p
                    change_port = port in h_b_p and (h_b_p[port] != w_b_p[port] or redo)
                    if new_port or change_port:
                        commands.append(f"interface {port}")
                        if change_port and port not in ports_cleared:
                            commands.append("no static-channel-group")
                            ports_cleared.append(port)
                        if w_g[g]:
                            commands.append(f"static-channel-group {g} member-filters")
                        else:
                            commands.append(f"static-channel-group {g}")
            if redo:
                for port in h_b_p:
                    if h_b_p[port] == g and port not in w_b_p:
                        commands.append(f"interface {port}")
                        if port not in ports_cleared:
                            commands.append("no static-channel-group")
                            ports_cleared.append(port)
                        if w_g[g]:
                            commands.append(f"static-channel-group {g} member-filters")
                        else:
                            commands.append(f"static-channel-group {g}")
        return commands

    def _state_deleted(self, have, want):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        h_b_p, w_b_p, h_g, w_g = self.gen_action_lists(have, want)
        ports_cleared = []
        for g in w_g:
            clear_count = 0
            for port in w_b_p:
                if w_b_p[port] == g and port in h_b_p and h_b_p[port] == g:
                    if port not in ports_cleared:
                        commands.append(f"interface {port}")
                        commands.append("no static-channel-group")
                        ports_cleared.append(port)
                        clear_count += 1
            if clear_count == 0:
                for port in h_b_p:
                    if h_b_p[port] == g:
                        if port not in ports_cleared:
                            commands.append(f"interface {port}")
                            commands.append("no static-channel-group")
                            ports_cleared.append(port)
                            clear_count += 1
        return commands

    def gen_action_lists(self, have, want):
        """ Return a list of ports that have to lose their static group, and
        a dictionary of ports that need a static group applied, based on the
        contents of have and want.
        :param: have: current configuration
        :param: want: desired configuration
        :rtype: dict, dict, dict, dict
        :returns:
        """
        have_by_port = {}
        want_by_port = {}
        have_groups = {}
        want_groups = {}
        for group in have:
            g_name = group.get("name")
            g_ports = group.get("members")
            if g_name:
                if g_name in have_groups:
                    self._module.fail_json(msg="duplicate group in current config")
                    return None, None, None, None
                have_groups[g_name] = group.get("member-filters")
                if g_ports:
                    for port in g_ports:
                        if port in have_by_port:
                            self._module.fail_json(msg="duplicate port in current config")
                            return None, None, None, None
                        have_by_port[port] = g_name
        if want:
            for group in want:
                g_name = group.get("name")
                g_ports = group.get("members")
                if g_name:
                    if g_name in want_groups:
                        self._module.fail_json(msg="duplicate group in desired config")
                        return None, None, None, None
                    want_groups[g_name] = group.get("member-filters")
                    if g_ports:
                        for port in g_ports:
                            if port in want_by_port:
                                self._module.fail_json(msg="duplicate port in desired config")
                                return None, None, None, None
                            want_by_port[port] = g_name
        return have_by_port, want_by_port, have_groups, want_groups

    def gen_commands_phase_1(self, h_b_p, w_b_p, h_g, w_g):
        """ Generate commands and list of ports which need to be taken out of a static channel group
        because of the member-filter parameter changing.
        :param: h_b_p: dictionary of have group by port
        :param: w_b_p: dictionary of want group by port
        :param: h_g: dictionary of have member-filters by group
        :param: w_g: dictionary of want member-filters by group
        :param: merge: is this a replace/override or merge?
        :param: delete: is this a delete?
        :rtype: list, list
        :returns: List of ports acted on and list of commands required to
                  take those ports out of static channel groups.
        """
        cmds = []
        p_rem = []
        for port in h_b_p:
            group = h_b_p[port]
            if group in w_g and h_g[group] != w_g[group]:
                cmds.append(f"interface {port}")
                cmds.append("no static-channel-group")
                p_rem.append(port)
        return p_rem, cmds
