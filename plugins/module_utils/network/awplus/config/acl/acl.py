#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_acl class
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
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
import re

class Acl(ConfigBase):
    """
    The awplus_acl class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'acl',
    ]

    def __init__(self, module):
        super(Acl, self).__init__(module)

    def get_acl_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        acl_facts = facts['ansible_network_resources'].get('acl')
        if not acl_facts:
            return []
        return acl_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()
        with open("output.txt", "w") as f:
            f.write("")
        existing_acl_facts = self.get_acl_facts()

        commands.extend(self.set_config(existing_acl_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_acl_facts = self.get_acl_facts()

        result['before'] = existing_acl_facts
        if result['changed']:
            result['after'] = changed_acl_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_acl_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_acl_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def check_parameters(self, state, want):
        """ Checks the incoming configuration and issues error
            messages based on the selected state

        :param state: the selected state
        :param want: the desired configuration as a dictionary
        :rtype: A bool
        :returns: True if the incoming configuration is empty, False otherwise
        """
        result = True  # remains true until user passes empty data
        with open("output.txt", "a") as f:
            f.write(f'{want}\n')
        if not (want is None or want[0].get('acls') is None):
            ace_1 = want[0].get('acls')[0].get('aces')
            if state in ('merged', 'replaced', 'overridden') or state == 'deleted' and ace_1:
                for item in want:
                    w_acls = item.get('acls')
                    for w_acl in w_acls:
                        # check if required parameters are given depending on the state
                        w_aces = w_acl.get('aces') if w_acl.get('aces') is not None else []
                        acl_type = w_acl.get('acl_type')
                        acl_name = w_acl.get('name')
                        for w_ace in w_aces:
                            action = w_ace.get('action')
                            ace_protocol = w_ace.get("protocols")
                            if action is None:
                                self._module.fail_json(
                                    msg=f"Missing aces parameter 'action' for state {state}"
                                )
                            if w_ace.get('source_addr') is None:
                                self._module.fail_json(
                                    msg=f"Missing aces parameter 'source_addr' for state {state}"
                                )
                            if w_ace.get('destination_addr') is None and acl_type != 'standard':
                                self._module.fail_json(
                                    msg=f"Missing aces parameter 'destination_addr' for state {state}"
                                )
                            if w_ace.get('protocols') is None and acl_type != 'standard':
                                self._module.fail_json(
                                    msg=f"Missing aces parameter 'protocols' for state {state}"
                                )
                            if acl_name.isnumeric() and ace_protocol in ('tcp', 'udp'):
                                self._module.fail_json(
                                    msg=f"Numbered acls are not supported for protocol: {ace_protocol}"
                                )
                            if acl_type == 'standard' and ace_protocol in ('tcp', 'udp'):
                                self._module.fail_json(
                                    msg=f"'Standard' ACLs don't support '{ace_protocol}' protocols"
                                )
                            if acl_type != 'hardware' and action not in ('permit', 'deny'):
                                self._module.fail_json(
                                    msg=f"Can't use action {action} with ACL type {acl_type}"
                                )
        else:
            result = False
        return result

    def generate_ace_commands(self, ace, acl_type=None):
        """ Generates commands for ACE component of ACL command

        :param ace: the desired ace configuration
        :rtype: A list
        :returns: the ace command necessary for the ACl command
        """
        action = ace.get('action').lower()
        protocol = ace.get('protocols')
        destination = ace.get('destination_addr')
        source = ace.get('source_addr')
        icmp_type = ace.get('ICMP_type_number')
        source_filter = ''
        dest_filter = ''
        command = []
        if protocol in ('tcp', 'udp'):
            source_protocol = ace.get('source_port_protocol')
            dest_protocol = ace.get('destination_port_protocol')
            if not source_protocol is None:

                source_type = list(source_protocol[0].keys())[0]
                source_port = None

                if source_type == 'range':
                    if acl_type == 'hardware':

                        source_range_conf = source_protocol[0].get('range')

                        if source_range_conf is not None and len(source_range_conf[0]) > 1:
                            start_port = source_range_conf[0].get('start')
                            end_port = source_range_conf[0].get('end')
                            source_port = f"{start_port} {end_port}"
                else:
                    source_port = source_protocol[0].get(f'{source_type}')

                if re.search(r'None', str(source_port) + str(source_type)):
                    source_filter = ''
                else:
                    source_filter = f"{source_type} {source_port}"
            if not dest_protocol is None:

                dest_type = list(dest_protocol[0].keys())[0]
                dest_port = None
                # with open("output.txt", "a") as f:
                #     f.write(f"{dest_type}\n\n")
                if dest_type == 'range':
                    if acl_type == 'hardware':

                        dest_range_conf = dest_protocol[0].get('range')
                        with open("output.txt", "a") as f:
                            f.write(f"{dest_range_conf}\n\n")
                        if dest_range_conf is not None and len(dest_range_conf[0]) > 1:
                            start_port = dest_range_conf[0].get('start')
                            end_port = dest_range_conf[0].get('end')
                            dest_port = f"{start_port} {end_port}"
                            with open("output.txt", "a") as f:
                                f.write(f"{start_port}  {end_port}\n\n")
                else:
                    dest_port = dest_protocol[0].get(f'{dest_type}')

                if re.search(r'None', str(dest_port) + str(dest_type)):
                    dest_filter = ''
                else:
                    dest_filter = f"{dest_type} {dest_port}"

        command.append(
            f"{action} {'' if protocol is None else protocol} "
            f"{source} {source_filter} {'' if destination is None else destination} {dest_filter}"
            f"{'icmp-type ' + str(icmp_type) if icmp_type is not None else ''}"
        )
        # with open("output.txt", "a") as f:
        #     f.write(f"ace_cmd {command}\n\n")
        return command[0]

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        state = self._module.params['state']
        commands = []
        result = self.check_parameters(state, want)

        if result:
            if state == 'overridden':
                commands = self._state_overridden(want, have)
            elif state == 'deleted':
                commands = self._state_deleted(want, have)
            elif state == 'merged':
                commands = self._state_merged(want, have)
            elif state == 'replaced':
                commands = self._state_replaced(want, have)

        # removing excess spaces from commands
        for index, command in enumerate(commands):
            commands[index] = (" ".join(command.split())).strip()
        with open("output.txt", "a") as f:
            f.write(f'{commands}\n')
        return commands

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        h_acls = have["acls"]
        for w_acls in want:
            for w_acl in w_acls.get('acls'):
                w_aces = w_acl.get('aces')
                w_acl_type = w_acl.get('acl_type').lower()
                for h_acl in h_acls:
                    if w_acl.get('name') == h_acl.get('name'):
                        w_afi = w_acls.get('afi').lower()
                        # hardware acls have a differant command layout
                        if w_acl_type == 'hardware' and w_acl.get('name').isnumeric():
                            if len(w_aces) > 1:
                                self._module.fail_json(msg="only one ace allowed for numbered hardware acls")
                            ace = w_aces[0]
                            w_name = w_acl.get('name')
                            ace_cmd = self.generate_ace_commands(ace, w_acl_type)
                            commands.append(f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list {w_name} {ace_cmd}")
                        else:
                            w_name = w_acl.get('name')
                            commands.append(
                                f"{'' if w_afi == 'ipv4' else 'ipv6'} "
                                f"access-list {w_acl_type if not w_name.isnumeric() else ''} "
                                f"{h_acl.get('name')}"
                            )
                            for h_ace in h_acl.get('ace'):
                                # with open("output.txt", "a") as f:
                                #     f.write(f"have {h_ace}\nthing {h_acl}\n")
                                ace_cmd = self.generate_ace_commands(h_ace, h_acl.get('type').lower())
                                commands.append(f'no {ace_cmd}')
                            for ace in w_aces:
                                ace_cmd = self.generate_ace_commands(ace, w_acl_type)
                                commands.append(ace_cmd)
        with open("output.txt", "a") as f:
            f.write(f'{commands}')
        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        h_acls = have["acls"] if have != [] else []

        # removing existing acls
        for h_acl in h_acls:
            h_acl_type = h_acl.get('type').lower()
            h_afi = h_acl.get('afi').lower()
            h_name = h_acl.get('name')
            if not h_name.isnumeric():
                cmd_type = h_acl_type
            else:
                cmd_type = ''
            commands.append(f"no {'' if h_afi == 'ipv4' else 'ipv6'} access-list {cmd_type} {h_name}")

        # adding new acls
        for item in want:
            w_acls = item.get('acls')
            w_afi = item.get('afi').lower()
            for w_acl in w_acls:
                w_acl_type = w_acl.get('acl_type').lower()
                w_aces = w_acl.get('aces')

                if w_acl_type == 'hardware' and w_acl.get('name').isnumeric():
                    w_name = w_acl.get('name')

                    if len(w_aces) > 1:
                        self._module.fail_json(msg="only one ace allowed for numbered hardware acls")

                    cmd = self.generate_ace_commands(w_aces[0], w_acl_type)
                    commands.append(f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list {w_name} {cmd}")
                else:
                    w_name = w_acl.get('name')

                    commands.append(
                        f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list "
                        f"{w_acl_type if not w_name.isnumeric() else ''} {w_name}"
                    )
                    for ace in w_aces:
                        ace_cmd = self.generate_ace_commands(ace, w_acl_type)
                        commands.append(ace_cmd)

        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        h_acls = have["acls"]

        for item in want:
            w_acls = item.get('acls')
            w_afi = item.get('afi').lower()

            for w_acl in w_acls:
                existing_acl = False
                w_aces = w_acl.get('aces')
                w_acl_type = w_acl.get('acl_type').lower()
                for h_acl in h_acls:
                    cmd = []
                    if w_acl.get('name') == h_acl.get('name'):  # an ace exists within the acl so modify the aces
                        existing_acl = True
                        w_acl_type = w_acl.get('acl_type').lower()
                        h_aces = h_acl.get('ace') if h_acl.get('ace') is not None else []

                        if w_acl_type == 'hardware' and w_acl.get('name').isnumeric():
                            w_name = w_acl.get('name')
                            # need to check that user only adds one ace for a numbered hardware acl
                            if len(w_aces) > 1:
                                self._module.fail_json(msg="only one ace allowed for numbered hardware acls")
                            ace_cmd = self.generate_ace_commands(w_aces[0], w_acl_type)
                            commands.append(f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list {w_name} {ace_cmd}")

                        else:
                            w_name = w_acl.get('name')
                            cmd.append(
                                f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list "
                                f"{w_acl_type if not w_name.isnumeric() else ''} {w_name}"
                            )
                            for ace in w_aces:
                                ace_dict = dict(ace)
                                ace_dict = utils.remove_empties(ace_dict)
                                ace_ID = ace.get('ace_ID')
                                if "ace_ID" in ace_dict:
                                    ace_dict.pop("ace_ID")  # need version of ace without ace_ID

                                else:
                                    self._module.fail_json(msg="'ace_ID' is required when merging aces")
                                if ace_dict not in h_aces:
                                    ace_cmd = self.generate_ace_commands(ace, w_acl_type)
                                    cmd.append(f'{ace_ID} {ace_cmd}')
                    if len(cmd) > 1:  # only add command if needed
                        commands.extend(cmd)

                if not existing_acl:  # add a new acl if nothing exists
                    w_acl_type = w_acl.get('acl_type').lower()
                    w_name = w_acl.get('name')
                    if w_acl_type == 'hardware' and w_name.isnumeric():
                        # need to check that user only adds one ace for a numbered hardware acl
                        if len(w_aces) > 1:
                            self._module.fail_json(msg="only one ace allowed for numbered hardware acls")

                        ace_cmd = self.generate_ace_commands(w_aces[0], w_acl_type)
                        commands.append(f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list {w_name} {ace_cmd}")
                    else:

                        commands.append(
                            f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list "
                            f"{w_acl_type if not w_name.isnumeric() else ''} {w_name}"
                        )
                        for ace in w_aces:
                            ace_cmd = self.generate_ace_commands(ace, w_acl_type)
                            commands.append(ace_cmd)

        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        h_acls = have["acls"]
        for item in want:
            w_acls = item.get('acls')
            w_afi = item.get('afi')

            for w_acl in w_acls:
                w_aces = w_acl.get('aces')
                for thing in h_acls:
                    if w_acl.get('name') == thing.get('name'):
                        w_acl_type = w_acl.get('acl_type').lower()
                        w_name = w_acl.get('name')
                        if w_aces is None or w_acl_type == 'hardware':  # delete the acl if no ace is provided
                            commands.append(
                                f"no {'' if w_afi == 'IPv4' else 'IPv6'} access-list "
                                f"{w_acl_type if not w_name.isnumeric() else ''} {w_name}"
                            )
                        else:  # delete the specified ace entry only
                            cmd = []
                            cmd.append(
                                f"{'' if w_afi == 'IPv4' else 'IPv6'} access-list "
                                f"{w_acl_type if not w_name.isnumeric() else ''} {w_name}"
                            )
                            for w_ace in w_aces:
                                for h_ace in thing.get('ace'):
                                    w_ace = utils.remove_empties(w_ace)
                                    if h_ace == w_ace:
                                        ace_cmd = self.generate_ace_commands(w_ace, w_acl_type)
                                        cmd.append(f"no {ace_cmd}")

                            if len(cmd) > 1:
                                commands.extend(cmd)
        return commands
