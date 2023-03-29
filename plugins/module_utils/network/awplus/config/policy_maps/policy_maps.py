# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_policy_maps class
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

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
    dict_diff,
    dict_merge,
    remove_empties,
)

import itertools
import re


class Policy_maps(ConfigBase):
    """
    The awplus_policy_maps class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'policy_maps',
    ]

    def __init__(self, module):
        super(Policy_maps, self).__init__(module)

    def get_policy_maps_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        policy_maps_facts = facts['ansible_network_resources'].get('policy_maps')
        if not policy_maps_facts:
            return []
        return policy_maps_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_policy_maps_facts = self.get_policy_maps_facts()
        commands.extend(self.set_config(existing_policy_maps_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_policy_maps_facts = self.get_policy_maps_facts()

        result['before'] = existing_policy_maps_facts
        if result['changed']:
            result['after'] = changed_policy_maps_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_policy_maps_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_policy_maps_facts
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
        want = [] if want is None else want
        for w_policy_map in want:
            for h_policy_map in have:
                if h_policy_map.get('name') == w_policy_map.get('name'):
                    commands.extend(self.do_replace(w_policy_map.get('name'), w_policy_map, h_policy_map))
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
        w_names = [w_map.get('name') for w_map in want]
        h_names = [h_map.get('name') for h_map in have]

        for h_policy_map in have:
            h_name = h_policy_map.get('name')
            if h_name in w_names:
                for w_policy_map in want:
                    w_name = w_policy_map.get('name')
                    if h_name == w_name:
                        commands.extend(self.do_replace(w_name, w_policy_map, h_policy_map))
            else:
                commands.extend(self.do_delete(h_name, {f"{h_name}": None}, h_policy_map))

        for w_policy_map in want:
            w_name = w_policy_map.get('name')
            if w_name not in h_names:
                commands.extend(self.do_config(w_name, w_policy_map, {}))
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
        for w_policy_map in want:
            w_item_name = w_policy_map.get('name')
            h_policy_map = {}
            for h_item in have:
                h_item_name = h_item.get('name')
                if h_item_name == w_item_name:
                    h_policy_map = h_item
            commands.extend(self.do_config(w_item_name, w_policy_map, h_policy_map))
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
        for w_policy_map in want:
            for h_policy_map in have:
                if w_policy_map.get('name') == h_policy_map.get('name'):
                    commands.extend(self.do_delete(w_policy_map.get('name'), w_policy_map, h_policy_map))
        return commands

    def do_delete(self, name, w_policy_map, h_policy_map):
        """ generate commands to delete a configuration

        :param name: name of the policy-map
        :param w_policy_map: the desired policy-map configuration as a dictionary
        :param h_policy_map: the current policy-map configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to achieve the desired policy-map configuration
        """
        cmd = []
        # dictionary of commands for each class, uses format:
        # {class_1: ['commands'], class_2: ['commands']}
        cmd_dict = dict()

        changed_items = dict_merge(h_policy_map, w_policy_map)
        changed_items = remove_empties(changed_items)
        w_policy_map = remove_empties(w_policy_map)
        h_policy_map = remove_empties(h_policy_map)

        for item in changed_items:
            # get the item that changed from want and have
            w_item = w_policy_map.get(item)
            h_item = h_policy_map.get(item)

            # generate commands for description, default_action and trust_dscp
            if item in ('description', 'default_action', 'trust_dscp') and w_item == h_item and w_item:
                cmd.insert(0,
                           f"{'no ' if item != 'default_action' else ''}{item.replace('_', '-').replace('-dscp', '')} "
                           f"{'permit' if item == 'default_action' else ''}"
                           )

            # generate commands for classifiers
            if item == 'classifiers':
                c_cmd = []
                class_names = []
                # get want and have classifiers
                w_classifiers = w_policy_map.get('classifiers') if w_policy_map.get('classifiers') is not None else []
                h_classifiers = h_policy_map.get('classifiers') if h_policy_map.get('classifiers') is not None else []
                # create a list of classes that are in want
                w_class_names = [w_classifier.get('name') for w_classifier in w_classifiers]

                for w_classifier in w_classifiers:
                    h_target = {}
                    # iterate through classes in have and assign class that matches the name of want to 'h_target'
                    for h_classifier in h_classifiers:
                        if h_classifier.get('name') == w_classifier.get('name'):
                            h_target = h_classifier

                    # get classifiers that have changed
                    c_classifiers = changed_items.get('classifiers')

                    for c_classifier in c_classifiers:
                        class_name = w_classifier.get('name')
                        if class_name not in cmd_dict:
                            cmd_dict[class_name] = []
                            class_names.append(class_name)
                        for c_item in c_classifier:

                            # check if changed_items exist in want and have and assign [] if want/have return None
                            w_class_item = w_classifier.get(c_item) if w_classifier.get(c_item) is not None else []
                            h_class_item = h_target.get(c_item) if h_target.get(c_item) else []

                            self.check_items(c_item, w_class_item)

                            # policer commands
                            if c_item == 'policer':
                                # round policer parameters
                                w_class_item = self.round_policer_values(w_class_item)
                                # change to [] if w_class_item is {}
                                w_class_item = {} if w_class_item == [] else w_class_item
                                if w_class_item == h_class_item and w_class_item or h_class_item and w_class_item.get('type') == 'none':
                                    pol_cmd = "no police"
                                    cmd_dict[class_name].append(pol_cmd) if pol_cmd not in cmd_dict[class_name] else None

                            # remark commands
                            if c_item == 'remark' and w_class_item and (w_class_item == h_class_item or h_class_item and w_class_item.get('apply') == 'none'):

                                apply = w_class_item.get('apply') if w_class_item.get('apply') != 'none' else h_class_item.get('apply')
                                remark_cmd = f"no remark new-cos {apply}"
                                cmd_dict[class_name].append(remark_cmd) if remark_cmd not in cmd_dict[class_name] else None

                            # remark_map commands
                            if c_item == 'remark_map' and w_class_item:

                                for h_remark_map in h_class_item:
                                    if h_remark_map in w_class_item and w_class_item:
                                        remark_map_cmd = (
                                            f"no remark-map bandwidth-class {h_remark_map.get('class_in')} to new-dscp "
                                            f"new-bandwidth-class"
                                        )
                                        cmd_dict[class_name].append(remark_map_cmd) if remark_map_cmd not in cmd_dict[class_name] else None

                            # storm_downtime commands
                            if c_item == 'storm_downtime':
                                if (w_class_item != 10 and w_class_item == h_class_item and w_class_item) or h_class_item and w_class_item == 0:
                                    sd_cmd = "storm-downtime 10"
                                    cmd_dict[class_name].append(sd_cmd) if sd_cmd not in cmd_dict[class_name] else None

                            # remaining storm commands
                            if c_item in ('storm_protection', 'storm_action', 'storm_rate', 'storm_window'):
                                if w_class_item == h_class_item and w_class_item or h_class_item and w_class_item in ('none', 0):
                                    s_cmd = f"no {c_item.replace('_', '-')}"
                                    cmd_dict[class_name].append(s_cmd) if s_cmd not in cmd_dict[class_name] else None

                            # pbr_next_hop commands
                            if c_item == 'pbr_next_hop' and (w_class_item == h_class_item and w_class_item or h_class_item and w_class_item == 'none'):
                                pbr_cmd = "no set ip next-hop"
                                cmd_dict[class_name].append(pbr_cmd) if pbr_cmd not in cmd_dict[class_name] else None

                # compile commands into one command
                for class_name in cmd_dict:
                    # check that class is valid and not default
                    if class_name != 'default' and self.check_classes(class_name):
                        if cmd_dict.get(class_name) and class_name in w_class_names:
                            cmd.append(f"class {class_name}")
                            cmd.extend(cmd_dict.get(class_name))
                        elif not cmd_dict.get(class_name) and class_name in w_class_names:
                            cmd.append(f"no class {class_name}")

        if cmd:
            cmd.insert(0, f"policy-map {name}")

        elif len(w_policy_map) <= 2:
            cmd.append(f"no policy-map {name}")
        return cmd

    def do_config(self, name, w_policy_map, h_policy_map):
        """ generate commands to merge a configuration

        :param name: name of the policy-map
        :param w_policy_map: the desired policy-map configuration as a dictionary
        :param h_policy_map: the current policy-map configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to achieve the desired policy-map configuration
        """
        cmd = []

        # dictionary of commands for each class, uses format:
        # {class_1: ['commands'], class_2: ['commands']}
        cmd_dict = dict()

        # get changed items to add and remove empty entries
        changed_items = dict_diff(h_policy_map, w_policy_map)
        w_policy_map = remove_empties(w_policy_map)
        h_policy_map = remove_empties(h_policy_map)
        changed_items = remove_empties(changed_items)
        for item in changed_items:
            # raise Exception('testing')
            w_item = w_policy_map.get(item)
            h_item = h_policy_map.get(item)

            # get want and have classifiers
            w_classifiers = w_policy_map.get('classifiers') if w_policy_map.get('classifiers') is not None else []
            h_classifiers = h_policy_map.get('classifiers') if h_policy_map.get('classifiers') is not None else []
            h_class_names = [h_classifier.get('name') for h_classifier in h_classifiers]

            # generate commands for description, default_action and trust_dscp
            if item in ('description', 'default_action', 'trust_dscp'):
                if w_item != h_item:
                    # generate commands for description, default_action and trust_dscp
                    cmd.insert(0,
                               f"{item.replace('_', '-') if item != 'trust_dscp' else 'trust dscp'} "
                               f"{changed_items.get(item).replace('_', '-') if item != 'trust_dscp' else ''}"
                               )

            if item == 'classifiers':
                h_target = {}

                # get h_classifier which has a matching name to want
                for w_classifier in w_classifiers:
                    for h_classifier in h_classifiers:
                        if h_classifier.get('name') == w_classifier.get('name'):
                            h_target = h_classifier

                    # get changed classifier items
                    c_classifiers = changed_items.get('classifiers')

                    for c_classifier in c_classifiers:
                        # get h_classifier which has a matching name to want
                        for w_classifier in w_classifiers:
                            if w_classifier.get('name') == c_classifier.get('name'):
                                w_target = w_classifier
                        for h_classifier in h_classifiers:
                            if h_classifier.get('name') == c_classifier.get('name'):
                                h_target = h_classifier
                        class_name = c_classifier.get('name')
                        if class_name not in cmd_dict:
                            cmd_dict[class_name] = []
                        for c_item in c_classifier:

                            # get want and have version of the changed item
                            w_class_item = w_target.get(c_item)if w_target.get(c_item) is not None else []
                            h_class_item = h_target.get(c_item) if h_target.get(c_item) is not None else []
                            c_item_value = c_classifier.get(c_item) if c_classifier.get(c_item) is not None else []

                            # check that want items are valid before continuing
                            self.check_items(c_item, w_class_item)

                            # remark commands
                            if c_item == 'remark' and w_class_item != h_class_item and w_class_item:

                                self.check_items(c_item, c_item_value)
                                new_cos = c_item_value.get('new_cos')
                                apply = c_item_value.get('apply')
                                h_apply = h_class_item.get('apply') if h_class_item != [] else None
                                if (not h_apply and apply != 'none') or h_class_item:
                                    remark_cmd = (
                                        f"{'no ' if apply == 'none' else ''}remark new-cos "
                                        f"{new_cos if apply != 'none' else ''} {apply if apply != 'none' else h_apply}"
                                    )
                                    cmd_dict[class_name].append(remark_cmd) if remark_cmd not in cmd_dict[class_name] else None

                            # policer commands
                            if c_item == 'policer':
                                # round policer items
                                w_class_item = self.round_policer_values(w_class_item)
                                h_class_item = self.round_policer_values(h_class_item)

                                w_class_item = {} if w_class_item == [] else w_class_item
                                if w_class_item != h_class_item:
                                    # check if policer should be added or removed
                                    if w_class_item.get('type') != 'none':
                                        # generate commands
                                        pol_cmd = self.do_policer_cmd(w_class_item)
                                        cmd_dict[class_name].append(pol_cmd) if pol_cmd not in cmd_dict[class_name] else None
                                    elif h_class_item:
                                        pol_cmd = 'no police'
                                        cmd_dict[class_name].append(pol_cmd) if pol_cmd not in cmd_dict[class_name] else None

                            # remark_map commands
                            if c_item == 'remark_map':
                                for w_remark_map in w_class_item:
                                    if w_remark_map not in h_class_item:
                                        # variable declarations
                                        w_class = w_remark_map.get('class_in')
                                        w_new_dscp = w_remark_map.get('new_dscp')
                                        w_new_class = w_remark_map.get('new_class')
                                        # sub-commands
                                        new_band_class_cmd = f"{'to' if w_new_dscp == -1 else ''} new-bandwidth-class {w_new_class}"
                                        new_dscp_cmd = f"to new-dscp {w_new_dscp}"
                                        # generate commands
                                        if (w_new_dscp != -1 or w_new_class != 'none') and not (w_new_dscp == -1 and w_new_class == 'none'):
                                            remark_map_cmd = (
                                                f"remark-map bandwidth-class {w_class} {new_dscp_cmd if w_new_dscp != -1 else ''} "
                                                f"{new_band_class_cmd if w_new_class != 'none' else ''}"
                                            )
                                            cmd_dict[class_name].append(remark_map_cmd) if remark_map_cmd not in cmd_dict[class_name] else None

                            # storm_downtime commands
                            if c_item == 'storm_downtime':
                                sd_cmd = None
                                if w_class_item != h_class_item:
                                    if w_class_item not in (10, 0):
                                        sd_cmd = f"storm-downtime {w_class_item}"
                                    elif w_class_item == 0 and h_class_item:
                                        sd_cmd = "storm-downtime 10"
                                if sd_cmd:
                                    cmd_dict[class_name].append(sd_cmd) if sd_cmd not in cmd_dict[class_name] else None

                            # remaining storm commands
                            if c_item in ('storm_protection', 'storm_action', 'storm_rate', 'storm_window'):
                                if w_class_item != h_class_item:
                                    if w_class_item and w_class_item not in ('none', 0):
                                        storm_cmd = f"{c_item.replace('_', '-')} {w_class_item if c_item != 'storm_protection' else ''}".replace('_', '')
                                        cmd_dict[class_name].append(storm_cmd) if storm_cmd not in cmd_dict[class_name] else None
                                        # cmd_dict[class_name][-1] = cmd_dict[class_name][-1].replace('_', '')
                                    elif w_class_item in ('none', 0) and h_class_item:
                                        storm_cmd = f"no {c_item.replace('_', '-')}"
                                        cmd_dict[class_name].append(storm_cmd) if storm_cmd not in cmd_dict[class_name] else None

                            # pbr_next_hop commands
                            if c_item == 'pbr_next_hop' and w_class_item:
                                if w_class_item != h_class_item and w_class_item != 'none' or w_class_item == 'none' and h_class_item != []:
                                    pbr_cmd = f"{'no ' if w_class_item == 'none' else ''}set ip next-hop {w_class_item if w_class_item != 'none' else ''}"
                                    cmd_dict[class_name].append(pbr_cmd) if pbr_cmd not in cmd_dict[class_name] else None

                # compile commands into one command
                for class_name in cmd_dict:
                    # check that class exists
                    if class_name != 'default' and self.check_classes(class_name):
                        if cmd_dict.get(class_name) or self.check_classes(class_name) and class_name not in h_class_names:
                            cmd.append(f"class {class_name}")
                        cmd.extend(cmd_dict.get(class_name))

        if cmd:
            if name:
                cmd.insert(0, f"policy-map {name}")
            else:
                cmd = []
        with open('output.txt', 'a') as f:
            f.write(f"{cmd}\n\n")

        return cmd

    def do_replace(self, name, w_policy_map, h_policy_map):
        """ generate commands to replace a configuration

        :param name: name of the policy-map
        :param w_policy_map: the desired policy-map configuration as a dictionary
        :param h_policy_map: the current policy-map configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to achieve the desired policy-map configuration
        """

        cmd = []

        # dictionary of commands for each class, uses format:
        # {class_1: ['commands'], class_2: ['commands']}
        cmd_dict = dict()

        # get changed items and remove emptys of changed_items.
        changed_items = dict_merge(dict_diff(h_policy_map, w_policy_map), dict_diff(w_policy_map, h_policy_map))
        changed_items = remove_empties(changed_items)

        # get classifiers of want and have
        w_classifiers = w_policy_map.get('classifiers') if w_policy_map.get('classifiers') is not None else []
        h_classifiers = h_policy_map.get('classifiers') if h_policy_map.get('classifiers') is not None else []

        # get lists of class names in want and have
        w_class_names = [w_classifier.get('name') for w_classifier in w_classifiers]
        h_class_names = [h_classifier.get('name') for h_classifier in h_classifiers]

        for item in changed_items:

            # perform replace for description, trust_dscp, default_action
            if item in ('description', 'trust_dscp', 'default_action') and h_policy_map.get(item) and not w_policy_map.get(item):
                cmd.insert(0, f"no {item.replace('_', '-').replace('-dscp', '')}")
            elif item in ('description', 'trust_dscp', 'default_action') and w_policy_map.get(item) is not None:
                if item in ('description', 'default_action'):
                    cmd.insert(0, f"{item.replace('_', '-')} {w_policy_map.get(item).replace('_', '-')}")
                else:
                    cmd.insert(0, "trust dscp")

            # perform replace for classifiers
            if item == 'classifiers':
                for classifier in changed_items.get('classifiers'):
                    w_target = {}
                    h_target = {}
                    c_cmd = []

                    # get w_classifier and h_classifier that has its class name in classifier
                    for w_classifier in w_classifiers:
                        if w_classifier.get('name') == classifier.get('name'):
                            w_target = w_classifier
                    for h_classifier in h_classifiers:
                        if h_classifier.get('name') == classifier.get('name'):
                            h_target = h_classifier

                    for class_item in classifier:
                        # get the w_item and h_item for each item in classifier
                        w_item = w_target.get(class_item) if w_target.get(class_item) is not None else {}
                        h_item = h_target.get(class_item) if h_target.get(class_item) is not None else {}
                        # check w_item to make sure items are allowed before continuing
                        self.check_items(class_item, w_item)

                        # add class_name to cmd_dict if not already in cmd_dict
                        class_name = classifier.get('name')
                        if class_name not in cmd_dict:
                            cmd_dict[class_name] = []

                        # policer commands
                        if class_item == 'policer':
                            # round policer items
                            w_item = self.round_policer_values(w_item)
                            h_item = self.round_policer_values(h_item)

                            p_type = w_item.get('type') if w_item != [] else None
                            if w_item and h_item != w_item and p_type != 'none':
                                # generate commands
                                p_cmd = self.do_policer_cmd(w_item)
                                cmd_dict[class_name].append(p_cmd) if p_cmd not in cmd_dict[class_name] else ''
                            elif h_item and not w_item or h_item and p_type == 'none':
                                p_cmd = "no police"
                                cmd_dict[class_name].append(p_cmd) if p_cmd not in cmd_dict[class_name] else ''
                        # remark commands
                        if class_item == 'remark':
                            # variable declarations
                            new_cos = w_item.get('new_cos')
                            apply = w_item.get('apply')

                            if w_item and h_item != w_item and apply != 'none':
                                # add/change
                                remark_cmd = f"remark new-cos {new_cos} {apply}"
                                cmd_dict[class_name].append(remark_cmd) if remark_cmd not in cmd_dict[class_name] else ''

                            elif h_item and not w_item or apply == 'none' and h_item:
                                # delete
                                remark_cmd = f"no remark new-cos {h_item.get('apply')}"
                                cmd_dict[class_name].append(remark_cmd) if remark_cmd not in cmd_dict[class_name] else ''

                        # remark_map commands
                        if class_item == 'remark_map':

                            # delete
                            for h_remark_map in h_item:

                                h_class = h_remark_map.get('class_in')
                                w_item = [] if w_item == {} else w_item
                                if h_remark_map not in w_item:
                                    rm_cmd = (
                                        f"no remark-map bandwidth-class {h_class} to new-dscp "
                                        f"new-bandwidth-class"
                                    )
                                    cmd_dict[class_name].append(rm_cmd) if rm_cmd not in cmd_dict.get(class_name) else ''

                            # add
                            for w_remark_map in w_item:

                                h_item = [] if h_item == {} else h_item
                                if w_remark_map in classifier.get(class_item) and w_remark_map not in h_item:
                                    # variable declaration
                                    w_class = w_remark_map.get('class_in')
                                    new_dscp = w_remark_map.get('new_dscp')
                                    new_class = w_remark_map.get('new_class')
                                    new_dscp_cmd = f"to new-dscp {new_dscp}"
                                    new_band_class_cmd = f"{'to ' if new_dscp == -1 else ''}new-bandwidth-class {new_class}"
                                    rm_cmd = (
                                        f"remark-map bandwidth-class {w_class} {new_dscp_cmd if new_dscp != -1 else ''} "
                                        f"{new_band_class_cmd if new_class != 'none' else ''}"
                                    )
                                    # only want to add command when (new_dscp XOR new_class)
                                    if (new_dscp != -1 or new_class != 'none') and not (new_dscp == -1 and new_class == 'none'):
                                        cmd_dict[class_name].append(rm_cmd) if rm_cmd not in cmd_dict.get(class_name) else ''

                        # storm_downtime commands
                        if class_item == 'storm_downtime':
                            if w_item and h_item != w_item:
                                sd_cmd = f"storm-downtime {w_item}"
                                cmd_dict[class_name].append(sd_cmd) if sd_cmd not in cmd_dict[class_name] else None
                            elif w_item == 0 and h_item:
                                cmd_dict[class_name].append("no storm-downtime")

                        # remaining storm commands
                        if class_item in ('storm_protection', 'storm_action', 'storm_rate', 'storm_window'):
                            if w_item and w_item != h_item and w_item not in ('none', 0):
                                st_cmd = f"{class_item.replace('_', '-')} {w_item if class_item != 'storm_protection' else ''}".replace('_', '')
                                cmd_dict[class_name].append(st_cmd) if st_cmd not in cmd_dict[class_name] else ''

                            elif h_item and not w_item or h_item and w_item in ('none', 0):
                                st_cmd = f"no {class_item.replace('_', '-')}"
                                cmd_dict[class_name].append(st_cmd) if st_cmd not in cmd_dict[class_name] else ''

                        # pbr_next_hop commands
                        if class_item == 'pbr_next_hop':
                            if w_item and w_item != h_item and w_item != 'none':
                                ip_cmd = f"set ip next-hop {w_item}"
                                cmd_dict[class_name].append(ip_cmd) if ip_cmd not in cmd_dict[class_name] else ''
                            elif h_item and not w_item or h_item and w_item == 'none':
                                ip_cmd = f"no set ip next-hop"
                                cmd_dict[class_name].append(ip_cmd) if ip_cmd not in cmd_dict[class_name] else ''

                # compile commands into one command
                for class_name in cmd_dict:
                    if class_name != 'default' and self.check_classes(class_name):

                        if cmd_dict.get(class_name) and class_name in w_class_names:
                            cmd.append(f"class {class_name}")
                            cmd.extend(cmd_dict.get(class_name))
                        elif class_name in h_class_names and class_name not in w_class_names:
                            cmd.append(f"no class {class_name}")

        if cmd:
            cmd.insert(0, f"policy-map {name}")
        return cmd

    def check_items(self, name, item):
        """ check incoming items to confirm validity
            issue error messages if items are either:
                - incomplete
                - out of allowed range

        :param name: name of the item
        :param w_policy_map: the contents of the item to check
        """
        # dictionary of allowed ranges for items
        valid_ranges = {'new_cos': {'lower': 0, 'upper': 7}, 'new_dscp': {'lower': -1, 'upper': 63},
                        'cir': {'lower': 1, 'upper': 100000000}, 'cbs': {'lower': 1, 'upper': 16777216},
                        'ebs': {'lower': 1, 'upper': 16777216}, 'pir': {'lower': 1, 'upper': 100000000},
                        'pbs': {'lower': 1, 'upper': 16777216}, 'storm_downtime': {'lower': 0, 'upper': 86400},
                        'storm_rate': {'lower': 1, 'upper': 40000000, 'reset': 0}, 'storm_window': {'lower': 100, 'upper': 60000}
                        }
        # string of items that are missing from item
        missing_params = ''
        # parameters that need values checked
        check_params = []

        if not item:
            return

        if name == 'remark':
            new_cos = item.get('new_cos')
            apply = item.get('apply')
            if not (new_cos and apply):
                missing_params += f"{'new_cos' if new_cos is None else ''}{' apply' if apply is None else ''}"
            else:
                check_params.append(('new_cos', new_cos))

        if name == 'remark_map':
            for remark_map in item:
                new_dscp = remark_map.get('new_dscp')
                Class = remark_map.get('class_in')
                new_class = remark_map.get('new_class')
                if not (Class and new_dscp and new_class):
                    missing_params += f"{'new_dscp' if new_dscp is None else ''}{' class' if Class is None else ''}{' new_class'if new_class is None else ''}"
                else:
                    check_params.append(('new_dscp', new_dscp))

        if name == 'policer':
            p_type = item.get('type')
            cir = item.get('cir')
            cbs = item.get('cbs')
            ebs = item.get('ebs')
            pir = item.get('pir')
            pbs = item.get('pbs')
            action = item.get('action')
            if not p_type:
                missing_params += "type"
            else:
                if p_type == 'single_rate' and (cir and cbs and ebs and action) is None:
                    missing_params += (
                        f"{'cir' if cir is None else ''}{' cbs' if cbs is None else ''}"
                        f"{' ebs' if ebs is None else ''}{' action' if action is None else ''}"
                    )
                if p_type == 'twin_rate' and not (cir and cbs and pir and pbs and action):
                    missing_params += (
                        f"{'cir' if not cir else ''}{' cbs' if not cbs else ''}"
                        f"{' pir' if not pir else ''}{' pbs' if not pbs else ''}{' action' if not action else ''}"
                    )
                check_params.extend([('cir', cir), ('cbs', cbs), ('pir', pir), ('pbs', pbs), ('ebs', ebs)])

        if name in ('storm_downtime', 'storm_rate', 'storm_window'):
            if item and item != 0:
                check_params.append((name, item))

        # check that parameters are in their allowed range
        for param in check_params:
            item = param[0]
            value = param[1]
            if value:
                item_high = valid_ranges.get(item).get('upper')
                item_low = valid_ranges.get(item).get('lower')
                if not (value >= item_low and value <= item_high):
                    self._module.fail_json(msg=f"value ({value}) for entry '{item}' not in allowed range {item_low}-{item_high}")

        # issue error messages if missing parameters are present
        if missing_params:
            self._module.fail_json(msg=f"parameter(s) '{missing_params}' missing from configuration in '{name}'")

    def check_classes(self, name):
        """ check whether a class exists

        :param name: name of the class to check
        :rtype: A bool
        :returns: True if a class exists, False otherwise
        """
        connection = self._connection
        result = connection.get(f"show class-map {name}")
        comp = re.search(r'CLASS-MAP-NAME: (\S+)', result)
        return True if comp else False

    def round_policer_values(self, item):
        """ rounds policer parameters (cir, cbs, pir, pbs)

        :param item: the policer item to round
        :rtype: A dict
        :returns: the rounded policer item
        """
        for name in item:
            value = item.get(name)
            rounded_item = False
            if value:
                if name in ('cir', 'pir'):
                    rounded_item = (value + 32) & ~63
                    rounded_item = 64 if rounded_item == 0 else rounded_item
                elif name in ('cbs', 'pbs', 'ebs'):
                    rounded_item = (value + 2048) & ~4095
                    rounded_item = 4096 if rounded_item == 0 else rounded_item
                if rounded_item:
                    item[name] = rounded_item
        return item

    def do_policer_cmd(self, item):
        """ generate policer commands

        :param item: the policer item
        :rtype: A list
        :returns: the required policer command
        """
        c_cmd = ''

        if item:
            type = item.get('type')

            # variable declarations
            cir = item.get('cir')
            cbs = item.get('cbs')
            ebs = item.get('ebs')
            pir = item.get('pir')
            pbs = item.get('pbs')

            if type == 'single_rate':
                c_cmd = (
                    f"police {type.replace('_', '-')} {cir} {cbs} "
                    f"{ebs} action {item.get('action').replace('_', '-')}"
                )
            elif type == 'twin_rate':
                c_cmd = (
                    f"police {type.replace('_', '-')} {cir} {pir} "
                    f"{cbs} {pbs} action {item.get('action').replace('_', '-')}"
                )
        return c_cmd
