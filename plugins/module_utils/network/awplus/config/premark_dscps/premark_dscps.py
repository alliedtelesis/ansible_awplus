#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_premark_dscps class
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
    dict_diff,
    dict_merge,
    remove_empties,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts


class Premark_dscps(ConfigBase):
    """
    The awplus_premark_dscps class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'premark_dscps',
    ]

    def __init__(self, module):
        super(Premark_dscps, self).__init__(module)

    def get_premark_dscps_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        premark_dscps_facts = facts['ansible_network_resources'].get('premark_dscps')
        if not premark_dscps_facts:
            return []
        return premark_dscps_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_premark_dscps_facts = self.get_premark_dscps_facts()
        commands.extend(self.set_config(existing_premark_dscps_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_premark_dscps_facts = self.get_premark_dscps_facts()

        result['before'] = existing_premark_dscps_facts
        if result['changed']:
            result['after'] = changed_premark_dscps_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_premark_dscps_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_premark_dscps_facts
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
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_overridden(**kwargs)
        elif state == 'deleted':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_deleted(**kwargs)
        elif state == 'merged':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_merged(**kwargs)
        elif state == 'replaced':
            kwargs = {'self': self, 'want': want, 'have': have}
            commands = self._state_replaced(**kwargs)
        return commands

    @staticmethod
    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        want = [] if not want else want
        for have_premark in have:
            for want_premark in want:
                w_dscp = want_premark.get('dscp_in')
                h_dscp = have_premark.get('dscp_in')
                if w_dscp == h_dscp:
                    commands.extend(self.replace_config(want_premark, have_premark))
        return commands

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        want = [] if not want else want
        w_dscps = [w_premark.get('dscp_in') for w_premark in want]
        for h_premark in have:
            h_dscp = h_premark.get('dscp_in')
            for w_premark in want:
                w_dscp = w_premark.get('dscp_in')
                if h_dscp == w_dscp:
                    commands.extend(self.replace_config(w_premark, h_premark))
            if h_dscp not in w_dscps:
                commands.extend(self.del_config({}, h_premark))
        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        want = [] if not want else want
        for h_premark in have:
            h_dscp = h_premark.get('dscp_in')
            for w_premark in want:
                w_dscp = w_premark.get('dscp_in')
                if w_dscp == h_dscp:
                    commands.extend(self.merge_config(w_premark, h_premark))
        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        want = [] if not want else want
        for h_premark in have:
            h_dscp = h_premark.get('dscp_in')
            for w_premark in want:
                w_dscp = w_premark.get('dscp_in')
                if w_dscp == h_dscp:
                    commands.extend(self.del_config(w_premark, h_premark))
        return commands

    def replace_config(self, w_premark, h_premark):
        """ generate a command to replace a premark-dscp map
        :param w_premark: the wanted premark-dscp map configuration
        :param h_premark: the current premark-dscp map configuration
        :rtype: A list
        :returns: the command necessary to replace the current premark-dscp map
        """
        cmd = []
        # sub-command declarations
        dscp_new_cmd = ''
        cos_new_cmd = ''
        class_new_cmd = ''

        # get changed items
        changed_items = dict_merge(dict_diff(w_premark, h_premark), dict_diff(h_premark, w_premark))
        changed_items = remove_empties(changed_items)

        # check want config for invalid values
        self.check_values(w_premark)

        dscp = w_premark.get('dscp_in')
        for c_item in changed_items:
            # get the value for want/have/changed_items
            c_val = changed_items.get(c_item)
            w_val = w_premark.get(c_item)
            h_val = h_premark.get(c_item)

            # generate sub-commands
            if c_item == 'dscp_new':
                if w_val:
                    dscp_new_cmd = f" new-dscp {w_val}"
                elif not w_val and h_val != dscp:
                    dscp_new_cmd = f" new-dscp {dscp}"
            elif c_item == 'cos_new':
                if c_val == w_val and c_val != h_val:
                    cos_new_cmd = f" new-cos {w_val}"
                elif not w_val and h_val != 0:
                    cos_new_cmd = f" new-cos 0"
            elif c_item == 'class_new':
                if w_val:
                    class_new_cmd = f" new-bandwidth-class {w_val}"
                elif not w_val and h_val != 'green':
                    class_new_cmd = f" new-bandwidth-class green"

        # generate a command if a sub-command has generated
        if (dscp_new_cmd or cos_new_cmd or class_new_cmd):
            cmd.append(
                f"mls qos map premark-dscp {dscp} to{dscp_new_cmd if dscp_new_cmd else ''}"
                f"{cos_new_cmd if cos_new_cmd else ''}{class_new_cmd if class_new_cmd else ''}"
            )
        return cmd

    def merge_config(self, w_premark, h_premark):
        """ generate a command to merge a premark-dscp map
        :param w_premark: the wanted premark-dscp map configuration
        :param h_premark: the current premark-dscp map configuration
        :rtype: A list
        :returns: the command necessary to merge the current premark-dscp map
        """
        cmd = []
        # declare sub-command variables
        dscp_new_cmd = ''
        cos_new_cmd = ''
        class_new_cmd = ''

        # get items to merge into config
        add_items = dict_diff(h_premark, w_premark)

        # check values in want for validity
        self.check_values(w_premark)

        if add_items:
            # declare variables before generating sub-commands
            dscp = w_premark.get('dscp_in')
            dscp_new = add_items.get('dscp_new')
            cos_new = add_items.get('cos_new')
            class_new = add_items.get('class_new')

            # generate sub-commands
            dscp_new_cmd = f" new-dscp {dscp_new}" if dscp_new != dscp else None
            cos_new_cmd = f" new-cos {cos_new}"
            class_new_cmd = f" new-bandwidth-class {class_new}" if class_new != 'green' else None

            # generate command
            cmd.append(
                f"mls qos map premark-dscp {dscp} to{dscp_new_cmd if dscp_new else ''}"
                f"{cos_new_cmd if cos_new else ''}{class_new_cmd if class_new else ''}"
            )
        return cmd

    def del_config(self, w_premark, h_premark):
        """ generate a command to delete a premark-dscp map
        :param w_premark: the wanted premark-dscp map configuration
        :param h_premark: the current premark-dscp map configuration
        :rtype: A list
        :returns: the command necessary to delete the current premark-dscp map
        """
        cmd = []
        # declare sub-command variables
        dscp_new_cmd = ''
        cos_new_cmd = ''
        class_new_cmd = ''

        # get items to delete
        del_items = dict_merge(h_premark, w_premark)

        # check items in want for validity
        self.check_values(w_premark)

        # variable declaration
        w_dscp = w_premark.get('dscp_in')
        h_dscp = h_premark.get('dscp_in')
        h_dscp_new = h_premark.get('dscp_new')
        h_cos_new = h_premark.get('cos_new')
        h_class_new = h_premark.get('class_new')

        # determine the number of Nones in w_premark
        num_nones = sum(1 for value in w_premark.values() if value is None)

        # create sub commands
        for item in del_items:
            w_item = w_premark.get(item)
            h_item = h_premark.get(item)
            if item == 'dscp_new' and w_item == h_item:
                dscp_new_cmd = f" new-dscp {w_dscp}"
            elif item == 'cos_new' and w_item == h_item:
                cos_new_cmd = " new-cos 0"
            elif item == 'class_new' and w_item == h_item:
                class_new_cmd = " new-bandwidth-class green"

        # generate commands
        if dscp_new_cmd or cos_new_cmd or class_new_cmd:
            cmd.append(
                f"mls qos map premark-dscp {w_dscp} to{dscp_new_cmd if dscp_new_cmd else ''}"
                f"{cos_new_cmd if cos_new_cmd else ''}{class_new_cmd if class_new_cmd else ''}"
            )
        elif (num_nones >= 3 or len(w_premark) == 0) and ((h_dscp_new != h_dscp) or (h_cos_new != 0) or (h_class_new != 'green')):
            cmd.append(f"no mls qos map premark-dscp {h_dscp}")
        return cmd

    def check_values(self, item):
        """ check that the incoming configuration is within the allowed ranges.
            Issue an error message when:
                - any integer value of item is out of range
        :param item: the configuration to be checked
        """

        # don't need to check dscp_in as this is already done in _state_{selected state}
        # before this function is called
        valid_ranges = {"dscp_new": {"lower": 0, "upper": 63}, "cos_new": {"lower": 0, "upper": 7}}

        for param in item:
            value = item.get(param)
            item_ranges = valid_ranges.get(param)
            if item_ranges and type(value) is int:
                item_low = item_ranges.get('lower')
                item_high = item_ranges.get('upper')
                if not (value >= item_low and value <= item_high):
                    self._module.fail_json(msg=f"value ({value}) for entry '{param}' not in allowed range {item_low}-{item_high}")
