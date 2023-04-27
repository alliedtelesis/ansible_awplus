#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_class_maps class
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


class Class_maps(ConfigBase):
    """
    The awplus_class_maps class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'class_maps',
    ]

    def __init__(self, module):
        super(Class_maps, self).__init__(module)

    def get_class_maps_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        class_maps_facts = facts['ansible_network_resources'].get('class_maps')
        if not class_maps_facts:
            return []
        return class_maps_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_class_maps_facts = self.get_class_maps_facts()
        commands.extend(self.set_config(existing_class_maps_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_class_maps_facts = self.get_class_maps_facts()

        result['before'] = existing_class_maps_facts
        if result['changed']:
            result['after'] = changed_class_maps_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_class_maps_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_class_maps_facts
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
        for w_class_map in want:
            for h_class_map in have:
                w_name = w_class_map.get('name')
                h_name = h_class_map.get('name')
                if w_name == h_name and h_name != 'default':
                    commands.extend(self._do_replace(w_name, w_class_map, h_class_map))
        return commands

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        w_names = []
        want = [] if want is None else want
        w_names = [w_class_map.get('name') for w_class_map in want]
        h_names = [h_class_map.get('name') for h_class_map in have]

        for h_class_map in have:
            h_name = h_class_map.get("name")
            if h_name in w_names:
                for w_class_map in want:
                    w_name = w_class_map.get('name')
                    if h_name == w_name and h_name != 'default':
                        # update current configuration
                        commands.extend(self._do_replace(w_name, w_class_map, h_class_map))
            elif h_name != 'default':
                # delete class-maps not in want
                commands.extend(self._do_delete(h_name, {f"{h_name}": None}, h_class_map))

        for w_class_map in want:
            w_name = w_class_map.get('name')
            if w_name not in h_names and w_name != 'default':
                # create new class-maps
                commands.extend(self._do_config(w_name, w_class_map, {}))
        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        want = [] if want is None else want

        for w_class_map in want:
            h_class_map = {}
            w_name = w_class_map.get('name')
            for item in have:
                item_name = item.get('name')
                if w_name == item_name:
                    h_class_map = item
            if h_class_map.get('name') != 'default':
                commands.extend(self._do_config(w_name, w_class_map, h_class_map))
        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        want = [] if want is None else want
        for w_class_map in want:
            w_name = w_class_map.get('name')
            for h_class_map in have:
                h_name = h_class_map.get('name')
                if w_name == h_name and h_name != 'default':
                    commands.extend(self._do_delete(w_name, w_class_map, h_class_map))
        return commands

    def check_ranges(self, name, value):
        """ Check that value received falls with the allowable range,
            fail the play if the value falls outside this range

        :param name: The name of the value to be checked
        :param value: The number to be checked against
        """
        valid_ranges = {'cos': {'lower': 0, 'upper': 7}, 'dscp': {'lower': 0, 'upper': 63},
                        'inner_cos': {'lower': 0, 'upper': 7}, 'inner_vlan': {'lower': 1, 'upper': 4094},
                        'vlan': {'lower': 1, 'upper': 4094}, 'ip_precedence': {'lower': 0, 'upper': 7}
                        }

        item = valid_ranges.get(name)
        if item and type(value) is int:
            value = int(value)
            low = item.get('lower')
            high = item.get('upper')
            if not (value >= low and value <= high):
                self._module.fail_json(msg=f"value ({value}) for entry {name} not in allowed range {low}-{high}")

    def _do_config(self, name, w_map, h_map):
        """ generate commands to update/create a configuration

        :param name: name of the class-map
        :param w_map: the desired class-map configuration as a dictionary
        :param h_map: the current class-map configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to achieve the desired class-map configuration
        """
        cmd = []

        w_tcp_flags = w_map.get("tcp_flags")

        # get changed items between h_map and w_map
        changed_items = dict_diff(h_map, w_map)

        if h_map.get('name') != w_map.get('name'):
            changed_items = w_map
        # remove items that are 'none' to obtain dictionary of values to update
        changed_items = remove_empties(changed_items)

        eth_for = w_map.get('eth_format')
        eth_pro = w_map.get('eth_protocol')

        if changed_items != {}:
            for item in changed_items:
                changed_item_value = changed_items.get(item)
                self.check_ranges(item, changed_item_value)
                h_item = h_map.get(item)
                # add new items
                if item == "tcp_flags":
                    flag_str_add = ''
                    flag_str_del = ''
                    h_item = {} if h_item is None else h_item
                    # get string of flags to add to config
                    for flag in w_tcp_flags:
                        if w_tcp_flags.get(flag) is True and h_item.get(flag) != w_tcp_flags.get(flag):
                            flag_str_add += f"{flag} "
                    if flag_str_add:
                        cmd.append(f"match {item.replace('_', '-')} {flag_str_add}")
                    # get string of flags to remove from config
                    for flag in w_tcp_flags:
                        if w_tcp_flags.get(flag) is False and h_item.get(flag) is not w_tcp_flags.get(flag):
                            flag_str_del += f"{flag} "
                    if flag_str_del:
                        cmd.append(f"no match {item.replace('_', '-')} {flag_str_del}")

                elif item not in ("name", "eth_format", "eth_protocol"):
                    cmd.append(f"match {item.replace('_', '-')} {changed_item_value}")
                # only add command if both eth_for and eth_pro are given
                elif eth_for is not None and eth_pro is not None:
                    cmd_str = f"match eth-format {eth_for} protocol {eth_pro}"
                    cmd.append(cmd_str) if cmd_str not in cmd else None

        if cmd or 'name' in changed_items:
            cmd.insert(0, f"class-map {name}")
        return cmd

    def _do_replace(self, name, w_map, h_map):
        """ generate commands to replace a current configuration

        :param name: name of the class-map
        :param w_map: the desired class-map configuration as a dictionary
        :param h_map: the current class-map configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to achieve the desired class-map configuration
        """

        cmd = []
        # get all changed items between h_map, w_map and w_map, h_map
        changed_items = dict_merge(dict_diff(h_map, w_map), dict_diff(w_map, h_map))

        w_map = remove_empties(w_map)
        h_map = remove_empties(h_map)

        w_tcp_flags = w_map.get("tcp_flags")
        eth_for = w_map.get('eth_format')
        eth_pro = w_map.get('eth_protocol')

        # supported flags
        valid_flags = ['urg', 'ack', 'rst', 'fin', 'psh', 'syn']

        # set flags that are not in want to false
        if w_tcp_flags:
            for flag in valid_flags:
                if flag not in w_tcp_flags:
                    w_tcp_flags[flag] = False
            w_tcp_flags = dict(sorted(w_tcp_flags.items()))
        else:
            w_tcp_flags = {'ack': False, 'fin': False, 'psh': False, 'rst': False, 'syn': False, 'urg': False}

        for item in changed_items:
            self.check_ranges(item, w_map.get(item))
            w_item = w_map.get(item)
            h_item = h_map.get(item)

            if item in ("eth_format", "eth_protocol"):
                # perform replace for eth format protocol if both parameters are given
                if "eth_format" in w_map and "eth_protocol" in w_map:
                    if w_item is not None and w_item is not h_item:
                        cmd_str = f"match eth-format {eth_for} protocol {eth_pro}"
                        if cmd_str not in cmd:
                            cmd.append(cmd_str)
                elif w_item is None:
                    cmd.append("no match eth-format protocol")

            elif item == "tcp_flags":
                add_flag = ''
                del_flag = ''
                h_item = {} if h_item is None else h_item
                # get flags to add or delete
                for flag in w_tcp_flags:
                    w_flag = w_tcp_flags.get(flag)
                    if w_flag is not h_item.get(flag):
                        if w_flag is True:
                            add_flag += f'{flag} '
                        else:
                            del_flag += f'{flag} '
                if add_flag:
                    cmd.append(f"match {item.replace('_', '-')} {add_flag}")
                if del_flag:
                    cmd.append(f"no match {item.replace('_', '-')} {del_flag}")
            else:
                # perform replace on other items
                if w_item is not None and w_item != h_item:
                    cmd.append(f"match {item.replace('_', '-')} {w_map.get(f'{item}')}")
                elif w_item is None:
                    cmd.append(f"no match {item.replace('_', '-')} {h_map.get(f'{item}') if item == 'access_group' else ''}")

        if cmd:
            cmd.insert(0, f"class-map {name}")
        # remove repeating commands
        cmd = list(dict.fromkeys(cmd))
        return cmd

    def _do_delete(self, name, w_map, h_map):
        """ generate commands to delete elements of an current configuration
            or deleting a class-map

        :param name: name of the class-map
        :param w_map: the desired class-map configuration as a dictionary
        :param h_map: the current class-map configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to achieve the desired class-map configuration
        """
        cmd = []
        # get changed elements
        changed_items = dict_merge(h_map, w_map)

        changed_items = remove_empties(changed_items)
        w_map = remove_empties(w_map)
        h_map = remove_empties(h_map)

        if w_map.get("tcp_flags") is None:
            w_map["tcp_flags"] = {}
        if h_map.get("tcp_flags") is None:
            h_map["tcp_flags"] = {}

        for item in changed_items:
            self.check_ranges(item, changed_items.get(item))

            # remove items
            w_item = w_map.get(item)
            h_item = h_map.get(item)
            if w_item is not None and w_item == h_item and item not in ('name', 'tcp_flags'):
                if item in ('eth_format', 'eth_protocol'):
                    cmd_str = "no match eth-format protocol"
                    cmd.append(cmd_str) if cmd_str not in cmd else None
                elif item == 'access_group':
                    cmd.append(f"no match access-group {h_item}")
                else:
                    cmd.append(f"no match {item.replace('_', '-')}")

            elif item == 'tcp_flags':
                diff_flags = dict_diff(h_map.get("tcp_flags"), w_map.get("tcp_flags"))
                flag_str_del = ''
                h_item = {} if h_item is None else h_item
                for flag in diff_flags:
                    flag_state = diff_flags.get(flag)
                    if flag_state is False and h_item.get(flag) != flag_state:
                        flag_str_del += f"{flag} "
                if flag_str_del:
                    cmd.append(f"no match {item.replace('_', '-')} {flag_str_del}")

        if cmd:
            cmd.insert(0, f"class-map {name}")
        elif len(w_map) < 3:
            cmd.insert(0, f"no class-map {name}")
        return cmd
