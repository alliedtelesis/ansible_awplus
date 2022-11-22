# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_openflow class
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

parm_to_keyword = {'inactivity_timer': 'inactivity',
                   'native_vlan': 'native vlan',
                   'fail_mode': 'failmode',
                   'datapath_id': 'datapath-id'}
fail_mode_commands = {'standalone': "openflow failmode standalone",
                      'secure': "no openflow failmode",
                      'secure_nre': "openflow failmode secure non-rule-expired"}


class Openflow(ConfigBase):
    """
    The awplus_openflow class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'openflow',
    ]

    def __init__(self, module):
        super(Openflow, self).__init__(module)

    def get_openflow_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        openflow_facts = facts['ansible_network_resources'].get('openflow')
        if not openflow_facts:
            return {}
        return openflow_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_openflow_facts = self.get_openflow_facts()
        commands.extend(self.set_config(existing_openflow_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_openflow_facts = self.get_openflow_facts()

        result['before'] = existing_openflow_facts
        if result['changed']:
            result['after'] = changed_openflow_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_openflow_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_openflow_facts
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
        if state in ("overridden", "merged", "replaced") and not want:
            self._module.fail_json(
                msg=f"value of config parameter must not be empty for state {state}")

        if state == 'overridden':
            commands = self._state_overridden(want, have)
        elif state == 'deleted':
            commands = self._state_deleted(want, have)
        elif state == 'merged':
            commands = self._state_merged(want, have)
        elif state == 'replaced':
            commands = self._state_replaced(want, have)
        return commands

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        self._do_controllers(want, have, "replaced", commands)
        self._do_ports(want, have, "merged", commands)
        self._do_other(want, have, "merged", commands)
        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        self._do_controllers(want, have, "overridden", commands)
        self._do_ports(want, have, "overridden", commands)
        self._do_other(want, have, "overridden", commands)
        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        self._do_controllers(want, have, "merged", commands)
        self._do_ports(want, have, "merged", commands)
        self._do_other(want, have, "merged", commands)
        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        self._do_controllers(want, have, "deleted", commands)
        self._do_ports(want, have, "deleted", commands)
        self._do_other(want, have, "deleted", commands)
        return commands

    def _controller_dicts(self, want, have):
        """
        Make dicts of controllers in want and have.
        """
        w_d = {}
        h_d = {}
        for cfg in ((want, w_d), (have, h_d)):
            if cfg[0].get('controllers'):
                for c in cfg[0].get('controllers'):
                    if c.get('name'):
                        cd = {}
                        for a in ('protocol', 'address', 'l4_port'):
                            cd[a] = c.get(a)
                        cfg[1][c.get('name')] = cd
        return w_d, h_d

    def _do_controllers(self, want, have, state, commands):
        """
        Handle actions for controllers.
        """
        # Get lists of controllers in want and have.
        wants, haves = self._controller_dicts(want, have)

        # Check all controllers in want - must have parameters for overridden and replaced,
        # and merged if it's a new controller. for deleted, controller should exist.
        for w_name in wants:
            if state in ('overridden', 'replaced') or (state == "merged" and w_name not in haves):
                cont_w = wants[w_name]
                if cont_w['address'] is None:
                    self._module.fail_json(msg="New controller address missing")
                if cont_w['protocol'] is None:
                    self._module.fail_json(msg="New controller protocol missing")
                if cont_w['l4_port'] is None:
                    self._module.fail_json(msg="New controller port missing")

        # Delete controllers based on parameters.
        for h_name in haves:
            if state in ("overridden", "replaced") or h_name in wants:
                commands.append(f"no openflow controller {h_name}")

        # That's it for deleted.
        if state == 'deleted':
            return

        # New controllers for overridden and replaced
        if state in ('overridden', 'replaced'):
            for w_name in wants:
                cont_w = wants[w_name]
                commands.append(
                    f"openflow controller {w_name} {cont_w['protocol']} "
                    f"{cont_w['address']} {cont_w['l4_port']}"
                )
            return

        # Merge - may need parameters from haves as well as wants.
        for w_name in wants:
            cont_w = wants[w_name]
            cont_h = haves.get(w_name)
            nc = {}
            for p in ('address', 'protocol', 'l4_port'):
                nc[p] = cont_w[p] if cont_w[p] is not None else cont_h[p]
            commands.append(
                f"openflow controller {w_name} {nc['protocol']}"
                f"{nc['address']} {nc['l4_port']}"
            )

    def _do_ports(self, want, have, state, commands):
        """
        Handle actions for ports.
        States "merged" and "replaced" are the same for ports. Caller should only use
        "overridden", "merged" and "deleted".
        """
        wants = want['ports'] if want.get('ports') is not None else []
        haves = have['ports'] if have.get('ports') is not None else []
        if state == "overridden":
            for port in haves:
                if port not in wants:
                    commands.append(f"interface {port}")
                    commands.append('no openflow')
        if state == "deleted":
            for port in wants:
                if port in haves:
                    commands.append(f"interface {port}")
                    commands.append('no openflow')
            return
        for port in wants:
            if port not in haves:
                commands.append(f"interface {port}")
                commands.append('openflow')

    def _do_other(self, want, have, state, commands):
        """
        Handle actions for other parameters.
        States "merged" and "replaced" are the same for other parameters. Caller should only use
        "overridden", "merged" and "deleted".
        Need special cases for all parameters.
        """
        # inactivity_timer, native_vlan, datapath_id - no default
        for p in ("inactivity_timer", "native_vlan", "datapath_id"):
            want_val = want.get(p)
            if (state == "deleted" and want_val is not None) or \
               (state == "overridden" and want_val is None):
                commands.append(f"no openflow {parm_to_keyword[p]}")
            elif want_val is not None:
                commands.append(f"openflow {parm_to_keyword[p]} {want_val}")

        # fail_mode - has a default but commands are irregular
        want_val = want.get("fail_mode")
        if (state == "deleted" and want_val is not None) or \
           (state == "overridden" and want_val is None):
            commands.append('no openflow failmode')
        elif want_val is not None:
            commands.append(fail_mode_commands[want_val])
