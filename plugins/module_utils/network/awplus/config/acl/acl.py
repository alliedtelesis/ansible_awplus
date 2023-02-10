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

        if not (want is None or want[0].get('acls') is None):
            ace_1 = want[0].get('acls')[0].get('aces')
            if state in ('merged', 'replaced', 'overridden') or state == 'deleted' and ace_1:
                for item in want:
                    w_acls = item.get('acls')
                    for w_acl in w_acls:
                        # check if required parameters are given depending on the state
                        w_aces = w_acl.get('aces') if w_acl.get('aces') is not None else []
                        acl_type = w_acl.get('acl_type')
                        for w_ace in w_aces:
                            if w_ace.get('action') is None:
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
        else:
            result = False
        return result

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
                for thing in h_acls:
                    if w_acl.get('name') == thing.get('name'):
                        w_afi = w_acls.get('afi').lower()
                        # hardware acls have a differant command layout
                        if w_acl_type == 'hardware' and w_acl.get('name').isnumeric():
                            if len(w_aces) > 1:
                                self._module.fail_json(msg="only one ace allowed for numbered hardware acls")
                            ace = w_aces[0]
                            w_name = w_acl.get('name')
                            w_action = ace.get('action').lower()
                            w_protocols = ace.get('protocols').lower()
                            w_icmp_type = ace.get('ICMP_type_number')
                            w_source = ace.get('source_addr')
                            w_destination = ace.get('destination_addr')
                            commands.append(
                                f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list {w_name} "
                                f"{w_action} {w_protocols} {w_source} {w_destination} "
                                f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                            )
                        else:
                            w_name = w_acl.get('name')
                            commands.append(
                                f"{'' if w_afi == 'ipv4' else 'ipv6'} "
                                f"access-list {w_acl_type if not w_name.isnumeric() else ''} "
                                f"{thing.get('name')}"
                            )
                            for h_ace in thing.get('ace'):
                                h_action = h_ace.get('action').lower()
                                h_protocols = h_ace.get('protocols')
                                h_dest_addr = h_ace.get('destination_addr')
                                h_source = h_ace.get('source_addr')
                                h_icmp_type = h_ace.get('ICMP_type_number')
                                commands.append(
                                    f"no {h_action} {'' if h_protocols is None else h_protocols.lower()} "
                                    f"{h_source} {'' if h_dest_addr is None else h_dest_addr.lower()} "
                                    f"{'icmp-type ' + str(h_icmp_type) if h_icmp_type is not None else ''}"
                                )
                            for ace in w_aces:
                                w_ace_action = ace.get('action').lower()
                                w_protocols = ace.get('protocols')
                                w_icmp_type = ace.get('ICMP_type_number')
                                w_destination = ace.get('destination_addr')
                                w_source = ace.get('source_addr')
                                commands.append(
                                    f"{w_ace_action} {'' if w_protocols is None else w_protocols.lower()} "
                                    f"{w_source} {'' if w_destination is None else w_destination} "
                                    f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                                )
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
                    w_action = w_aces[0].get('action').lower()
                    w_protocol = w_aces[0].get('protocols').lower()
                    w_dest_addr = w_aces[0].get('destination_addr')
                    w_source = w_aces[0].get('source_addr')
                    w_icmp_type = w_aces[0].get('ICMP_type_number')
                    if len(w_aces) > 1:
                        self._module.fail_json(msg="only one ace allowed for numbered hardware acls")
                    commands.append(
                        f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list {w_name} "
                        f"{w_action} {w_protocol} {w_source} {w_dest_addr} "
                        f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                    )
                else:
                    w_name = w_acl.get('name')
                    commands.append(
                        f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list "
                        f"{w_acl_type if not w_name.isnumeric() else ''} {w_name}"
                    )
                    for ace in w_aces:
                        w_action = ace.get('action').lower()
                        w_protocol = ace.get('protocols')
                        w_destination = ace.get('destination_addr')
                        w_source = ace.get('source_addr')
                        w_icmp_type = ace.get('ICMP_type_number')
                        commands.append(
                            f"{w_action} {'' if w_protocol is None else w_protocol} "
                            f"{w_source} {'' if w_destination is None else w_destination} "
                            f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                        )
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
                            w_action = w_aces[0].get('action').lower()
                            w_protocol = w_aces[0].get('protocols').lower()
                            w_icmp_type = w_aces[0].get('ICMP_type_number')
                            w_source = w_aces[0].get('source_addr')
                            w_destination = w_aces[0].get('destination_addr')
                            # need to check that user only adds one ace for a numbered hardware acl
                            if len(w_aces) > 1:
                                self._module.fail_json(msg="only one ace allowed for numbered hardware acls")
                            commands.append(
                                f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list {w_name} "
                                f"{w_action} {w_protocol} {w_source} {w_destination} "
                                f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                            )

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
                                w_action = ace.get('action').lower()
                                w_protocol = ace.get('protocols').lower()
                                w_destination = ace.get('destination_addr')
                                w_source = ace.get('source_addr')
                                w_icmp_type = ace.get('ICMP_type_number')
                                if "ace_ID" in ace_dict:
                                    ace_dict.pop("ace_ID")  # need version of ace without ace_ID

                                else:
                                    self._module.fail_json(msg="'ace_ID' is required when merging aces")
                                if ace_dict not in h_aces:
                                    cmd.append(
                                        f"{ace_ID} {w_action} {'' if w_protocol is None else w_protocol} "
                                        f"{w_source} {'' if w_destination is None else w_destination} "
                                        f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                                    )
                    if len(cmd) > 1:  # only add command if needed
                        commands.extend(cmd)

                if not existing_acl:  # add a new acl if nothing exists
                    w_acl_type = w_acl.get('acl_type').lower()
                    w_name = w_acl.get('name')
                    if w_acl_type == 'hardware' and w_name.isnumeric():
                        # need to check that user only adds one ace for a numbered hardware acl
                        if len(w_aces) > 1:
                            self._module.fail_json(msg="only one ace allowed for numbered hardware acls")

                        w_action = w_aces[0].get('action').lower()
                        w_protocol = w_aces[0].get('protocols').lower()
                        w_destination = w_aces[0].get('destination_addr')
                        w_source = w_aces[0].get('source_addr')
                        w_icmp_type = w_aces[0].get('ICMP_type_number')
                        commands.append(
                            f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list {w_name} "
                            f"{w_action} {w_protocol} {w_source} {w_destination} "
                            f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                        )
                    else:

                        commands.append(
                            f"{'' if w_afi == 'ipv4' else 'ipv6'} access-list "
                            f"{w_acl_type if not w_name.isnumeric() else ''} {w_name}"
                        )
                        for ace in w_aces:
                            w_action = ace.get('action')
                            w_protocol = ace.get('protocols')
                            w_destination = ace.get('destination_addr')
                            w_source = ace.get('source_addr')
                            w_icmp_type = ace.get('ICMP_type_number')
                            commands.append(
                                f"{w_action} {'' if w_protocol is None else w_protocol} "
                                f"{w_source} {'' if w_destination is None else w_destination} "
                                f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                            )
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
                                w_action = w_ace.get('action')
                                w_protocol = w_ace.get('protocols')
                                w_destination = w_ace.get('destination_addr')
                                w_source = w_ace.get('source_addr')
                                w_icmp_type = w_ace.get('ICMP_type_number')
                                for h_ace in thing.get('ace'):
                                    w_ace = utils.remove_empties(w_ace)
                                    if h_ace == w_ace:
                                        cmd.append(
                                            f"no {w_action} {'' if w_protocol is None else w_protocol} "
                                            f"{w_source} {'' if w_destination is None else w_destination} "
                                            f"{'icmp-type ' + str(w_icmp_type) if w_icmp_type is not None else ''}"
                                        )
                            if len(cmd) > 1:
                                commands.extend(cmd)
        return commands
