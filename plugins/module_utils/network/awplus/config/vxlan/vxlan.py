#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_vxlan class
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
from ansible.module_utils.six import iteritems
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts


class Vxlan(ConfigBase):
    """
    The awplus_vxlan class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'vxlan',
    ]

    def __init__(self, module):
        super(Vxlan, self).__init__(module)
        self.change_counts = dict(vlans={}, vnis={})

    def get_vxlan_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        vxlan_facts = facts['ansible_network_resources'].get('vxlan')
        if not vxlan_facts:
            return []
        return vxlan_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        commands = list()

        existing_vxlan_facts = self.get_vxlan_facts()
        commands.extend(self.set_config(existing_vxlan_facts))

        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_vxlan_facts = self.get_vxlan_facts()

        result['before'] = existing_vxlan_facts
        if result['changed']:
            result['after'] = changed_vxlan_facts

        return result

    def set_config(self, existing_vxlan_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_vxlan_facts
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
        commands = []
        state = self._module.params['state']

        if not want and state in ('merged', 'replaced', 'deleted'):
            self._module.fail_json(msg="At least one mapping is required.")

        if state in ('merged', 'replaced', 'overridden') and want and want.get('l2_vnis'):
            for w_map in want.get('l2_vnis'):
                # Check that ranges are correct.
                if not 0 < w_map['vlan'] < 4095:
                    self._module.fail_json(msg="VLAN must be between 1 and 4094 inclusively.")
                elif not 0 < w_map['vni'] < 16777216:
                    self._module.fail_json(msg="VNI must be between 1 and 16777215 inclusively.")

        if state == 'overridden':
            commands.extend(self._state_overridden(want, have))
        elif state == 'deleted':
            commands.extend(self._state_deleted(want, have))
        elif state == 'merged':
            commands.extend(self._state_merged(want, have))
        elif state == 'replaced':
            commands.extend(self._state_replaced(want, have))

        self._validate_duplicates(have)

        return commands

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        commands.extend(self._global_config(have))
        commands.extend(self._clear_config("replaced", want.get("l2_vnis"), have.get("l2_vnis")))
        commands.extend(self._set_config(want.get("l2_vnis"), have.get("l2_vnis")))

        if commands:
            commands.insert(0, "nvo vxlan")
        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []    

        if not want or not want.get("l2_vnis"):
            commands.extend(self._clear_config("deleted", have.get("l2_vnis"), have.get("l2_vnis")))
        else:
            commands.extend(self._global_config(have))
            commands.extend(self._clear_config("overridden", want.get("l2_vnis"), have.get("l2_vnis")))
            commands.extend(self._set_config(want.get("l2_vnis"), have.get("l2_vnis")))

        if commands:
            commands.insert(0, "nvo vxlan")
        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        commands.extend(self._global_config(have))
        commands.extend(self._clear_config("merged", want.get("l2_vnis"), have.get("l2_vnis")))
        commands.extend(self._set_config(want.get("l2_vnis"), have.get("l2_vnis")))

        if commands:
            commands.insert(0, "nvo vxlan")
        return commands

    def _global_config(self, have):
        """
        Generates commands based on the current configuration only
        so that dynamic (bgp-evpn mode) vxlan commands can bthe current configuration as a dictionarye run
        
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        if have.get("internal").get("host_reachability") is None:
            commands.append("host-reachability-protocol evpn-bgp")
        if have.get("internal").get("source_interface") is None:
            commands.append("source-interface lo")
        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        commands.extend(self._global_config(have))
        commands.extend(self._clear_config("deleted", want.get("l2_vnis"), have.get("l2_vnis")))

        if commands:
            commands.insert(0, "nvo vxlan")
        return commands

    def _set_config(self, want, have):
        """
        Docstring for _set_config
        """
        commands = []
        for w_map in want:
            add = True
            for h_map in have:
                if w_map.get("vlan") == h_map.get("vlan") and w_map.get("vni") == h_map.get("vni"):
                    add = False
            if add == True:
                commands.append(f"map-access vlan {w_map.get("vlan")} vni {w_map.get("vni")}")
                self._update_change_counts(w_map.get("vlan"), w_map.get("vni"), 1)   

        return commands

    def _clear_config(self, state, want, have):
        """
        Generate commands to clear config that must be cleared.
        
        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        for h_map in have:
            matching_vlan = False
            matching_vni = False
            for w_map in want:
                if w_map.get("vlan") == h_map.get("vlan"):
                    matching_vlan = True
                    if w_map.get("vni") == h_map.get("vni"):
                        matching_vni = True

            removed = False
            if state in ('merged', 'replaced'):
                if matching_vlan and not matching_vni:
                    removed = True
            elif state == 'deleted':
                if matching_vlan:
                    removed = True
            elif state == 'overridden':
                if not matching_vlan or matching_vlan and not matching_vni:
                    removed = True

            if removed:
                commands.append(f"no map-access vlan {h_map.get("vlan")}")
                self._update_change_counts(h_map.get("vlan"), h_map.get("vni"), -1)   
        
        return commands

    def _update_change_counts(self, vlan, vni, amount):
        """
        Updates the change counts dict to count how many of each
        specific VLAN and VNI ID you will gain/lose through the 
        changes actually made.the current configuration as a dictionary

        :param vlan: The VLAN id
        :param vni: The VNI id 
        :param amount: The amount to change by (+1/-1)
        """
        current_vlan_count = self.change_counts['vlans'].get(vlan, 0)
        current_vni_count = self.change_counts['vnis'].get(vni, 0)
        self.change_counts['vlans'][vlan] = current_vlan_count + amount
        self.change_counts['vnis'][vni] = current_vni_count + amount

    def _validate_duplicates(self, have):
        """
        Checks for duplicate vlans/vnis and raises an error if there will be one 
        based off of the given have and want
        
        :param have: the current configuration as a dictionary
        """
        # Count the number of uses of each vlan and vni in the current config
        have_counts = dict(vlans={}, vnis={})
        for h_map in have.get('l2_vnis'):
            current_vlan_count = have_counts['vlans'].get(h_map['vlan'])
            current_vni_count = have_counts['vnis'].get(h_map['vni'])
            have_counts['vlans'][h_map['vlan']] = current_vlan_count + 1 if current_vlan_count else 1
            have_counts['vnis'][h_map['vni']] = current_vni_count + 1 if current_vni_count else 1

        # Check that the sum of have counts and the change counts are at most 1
        # e.g., that there is no duplicate vlan/vni
        vlan_ids = set(have_counts['vlans'].keys()).union(set(self.change_counts['vlans'].keys()))
        vni_ids = set(have_counts['vnis'].keys()).union(set(self.change_counts['vnis'].keys()))
        for vlan in vlan_ids:
            total = have_counts['vlans'].get(vlan, 0) + self.change_counts['vlans'].get(vlan, 0)
            if total > 1:
                self._module.fail_json(msg="Each VLAN can only be used for a single mapping.")
        for vni in vni_ids:
            total = have_counts['vnis'].get(vni, 0) + self.change_counts['vnis'].get(vni, 0)
            if total > 1:
                self._module.fail_json(msg="Each VNI can only be used for a single mapping.")
