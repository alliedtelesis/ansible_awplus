#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_static_route class
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
    validate_ip_v6_address,
    validate_ip_address,
)

from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts

from copy import deepcopy

import re

from ipaddress import (
    IPv4Network,
    NetmaskValueError
)

# list of IPs that this module is not allowed to modify.
banned_ips = [
    '1.1.1.0/24',
    '10.33.0.0/16',
    '10.33.22.0/24',
    '10.37.0.0/16',
    '10.37.153.0/27'
]


class Static_route(ConfigBase):
    """
    The awplus_static_route class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'static_route',
    ]

    def __init__(self, module):
        super(Static_route, self).__init__(module)

    def get_static_route_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        static_route_facts = facts['ansible_network_resources'].get('static_route')
        if not static_route_facts:
            return []
        return static_route_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_static_route_facts = self.get_static_route_facts()
        commands.extend(self.set_config(existing_static_route_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_static_route_facts = self.get_static_route_facts()

        result['before'] = existing_static_route_facts
        if result['changed']:
            result['after'] = changed_static_route_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_static_route_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_static_route_facts
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
        have = {} if not have else have
        want = {} if not want else want
        for h_item in have:
            for w_item in want:
                self._check_config(w_item)
                w_addr = self._get_address(w_item)
                h_addr = h_item.get('address')
                w_next_hop = w_item.get('next_hop').replace("null", "NULL")
                h_next_hop = h_item.get('next_hop').replace("null", "NULL") if w_item.get("next_hop") else None

                if w_addr == h_addr and h_next_hop == w_next_hop and w_addr not in banned_ips:
                    commands.extend(self._change_config(w_item, h_item, replaced=True))
        return commands

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        have = {} if not have else have
        want = {} if not want else want

        # get a list of "(address, next_hop)" for each item in want
        h_names = [(h_item.get("address"), h_item.get("next_hop").replace("null", "NULL")) for h_item in have]
        w_names = []
        for w_item in want:
            self._check_config(w_item)
            w_addr = self._get_address(w_item)
            w_names.append((w_addr, w_item.get("next_hop").replace("null", "NULL") if w_item.get("next_hop") else None))

        # generate commands
        for h_item in have:
            h_addr = h_item.get("address")
            h_next_hop = h_item.get("next_hop").replace("null", "NULL")
            if (h_addr, h_next_hop) in w_names:
                for w_item in want:
                    self._check_config(w_item)
                    w_addr = self._get_address(w_item)
                    w_next_hop = w_item.get("next_hop").replace("null", "NULL") if w_item.get("next_hop") else None
                    if w_addr == h_addr and w_next_hop == h_next_hop:
                        # replace the items in have to match want
                        commands.extend(self._change_config(w_item, h_item, replaced=True))
            else:
                # delete any routes that are not in want
                commands.extend(self._clear_config(h_item))

        for w_item in want:
            # add routes missing from have but in want
            self._check_config(w_item)
            w_addr = self._get_address(w_item)
            w_next_hop = w_item.get("next_hop").replace("null", "NULL") if w_item.get("next_hop") else None
            w_afi = w_item.get("afi")
            if (w_addr, w_next_hop) not in h_names:
                h_config = {"afi": w_afi, "address": w_addr, "next_hop": w_next_hop, "new": True}
                commands.extend(self._change_config(w_item, h_config))
        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        have = {} if not have else have
        want = {} if not want else want

        h_names = [(h_item.get("address"), h_item.get("next_hop").replace("null", "NULL")) for h_item in have]

        # generate commands
        for w_item in want:
            self._check_config(w_item)
            w_addr = self._get_address(w_item)
            w_next_hop = w_item.get("next_hop").replace("null", "NULL") if w_item.get("next_hop") else None
            w_name = (w_addr, w_next_hop)
            w_afi = w_item.get("afi")
            # check if a static route already exists, if not, add it.
            if w_name not in h_names:
                # make new template for have and pass through new = True to indicate a new config
                h_config = {"afi": w_afi, "address": w_addr, "next_hop": w_next_hop, "new": True}
                commands.extend(self._change_config(w_item, h_config))
                continue

            for h_item in have:
                h_config = {}
                h_addr = h_item.get('address')
                h_next_hop = h_item.get("next_hop").replace("null", "NULL")

                # generate the commands to merge a config
                if w_addr == h_addr and w_next_hop == h_next_hop:
                    commands.extend(self._change_config(w_item, h_item))
        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        have = {} if not have else have
        want = {} if not want else want

        # generate commands
        for h_item in have:
            h_addr = h_item.get("address")
            h_next_hop = h_item.get("next_hop").replace("null", "NULL")

            # delete items in single static route
            for w_item in want:
                self._check_config(w_item)
                w_item = remove_empties(w_item)
                w_addr = self._get_address(w_item)
                w_next_hop = w_item.get("next_hop").replace("null", "NULL") if w_item.get("next_hop") else None
                if w_addr == h_addr and (w_next_hop == h_next_hop or len(w_item) <= 2):
                    # determine if there are items to remove from a static route
                    deletable_items = [item in w_item for item in ('vrf', 'admin_distance', 'description', 'source_address')]

                    # if there is no removable items in want, the user must want the route removed
                    if True not in deletable_items:
                        to_remove = w_item if len(w_item) <= 2 else h_item
                        command = self._clear_config(to_remove)
                        commands.extend(command) if command[0] not in commands else None
                        continue
                    commands.extend(self._change_config(w_item, h_item, deleted=True))
        return commands

    def _get_address(self, item):
        """ Obtain the IP address of the incoming configuration

        :param item: the configuration to get the address from
        :rtype: A string
        :returns: the address of the static route
        """
        addr = item.get("address")
        if ' ' in addr:
            split_addr = addr.split(' ')
            # check that the netmask is valid
            addr_prefix = IPv4Network(f"0.0.0.0/{split_addr[1]}").prefixlen

            addr = f"{split_addr[0]}/{addr_prefix}"
        return addr

    def _check_vrf(self, vrf):
        """ Checks that the VRF is configured on the target device

        :param vrf: the name of the VRF to check
        :rtype: A bool
        :returns: True if the VRF exists on the device, False otherwise
        """
        connection = self._connection
        result = connection.get(f"show ip vrf {vrf}")
        pattern = f'VRF {vrf} does not exist'
        comp = re.search(pattern, result)
        return True if not comp else False

    def _check_config(self, w_item):
        """ Checks that the incoming config is valid
            Issue Errors when:
                - Invalid IPv4/IPv6 addresses is given
                - Incorrect address/afi combination is given
                - Invalid Netmask is given
                - Non-existing VRF is given
                - Out of range value for admin_distance is given
        :param w_item: the configuration to check
        """
        w_addr = w_item.get("address")
        w_afi = w_item.get("afi")
        w_vrf = w_item.get("vrf")
        w_admin_dist = w_item.get("admin_distance")

        # check that the address and afi are valid
        result = False
        if ('/' in w_addr):
            w_addr = w_addr.split('/')[0]
            if w_afi == "IPv6":
                result = validate_ip_v6_address(w_addr)
            else:
                result = validate_ip_address(w_addr)
        elif w_afi == 'IPv4' and ' ' in w_addr:
            w_addr = w_addr.split(' ')

            try:
                # check that the netmask is valid
                IPv4Network(f"0.0.0.0/{w_addr[1]}").prefixlen

            except NetmaskValueError:
                self._module.fail_json(msg=f"invalid netmask '{w_addr[1]}")

            result = validate_ip_address(w_addr[0])

        if not result:
            self._module.fail_json(msg="incorrect address/afi in config")

        if w_vrf and not self._check_vrf(w_vrf):
            self._module.fail_json(msg=f"unknown vrf '{w_vrf}'")

        if w_admin_dist:
            if not (w_admin_dist >= 1 and w_admin_dist <= 255):
                self._module.fail_json(msg=f"value '{w_admin_dist}' for admin_distance not in allowed range 1-255")

    def _clear_config(self, item):
        """ generate commands to clear a configuration from the target device

        :param item: the configuration to clear from the target device
        :rtype: A list
        :returns: the commands necessary to clear a static route from the target device configuration
        """
        commands = []
        next_hop_prefix = ''
        w_afi = item.get("afi")
        source = item.get("source_address")
        vrf = item.get("vrf")
        afi_prefix = "ip" if w_afi == "IPv4" else w_afi.lower()
        source_prefix = f" {source}" if source and w_afi == "IPv6" else ""
        vrf_prefix = f" vrf {vrf}" if vrf else ""
        address = self._get_address(item)

        if item.get("next_hop"):
            next_hop_prefix = f" {item.get('next_hop').replace('null', 'NULL')}"

        if address not in banned_ips:
            commands.append(
                f"no {afi_prefix} route{vrf_prefix} {item.get('address')}"
                f"{source_prefix}{next_hop_prefix if next_hop_prefix else ''}"
            )
        return commands

    def _change_config(self, w_item, h_item, replaced=False, deleted=False):
        """ generate commands to change a configuration

        :param w_item: the desired static route configuration as a dictionary
        :param h_item: the current static route configuration as a dictionary
        :param replaced: Flag used to signal a replaced action
        :param deleted: Flag used to signal a deleted action

        :rtype: A list
        :returns: the commands necessary to achieve the desired policy-map configuration
        """
        # get items that have changed
        diff1 = dict_diff(h_item, w_item)
        diff2 = dict_diff(w_item, h_item)
        diff = dict_merge(diff2, diff1)

        if deleted:
            # get a dictionary of identical values between want and have.
            # discard anything else, including address, afi, and next_hop
            diff = remove_empties(dict_merge(h_item, w_item))
            temp_diff = deepcopy(diff)
            for item in diff:
                if item in ("address", "afi", "next_hop") or h_item.get(item) != w_item.get(item):
                    temp_diff.pop(item)
            diff = deepcopy(temp_diff)

        # declare variables
        changed = False  # determines if a command should be generated
        commands = []

        h_admin_dist = h_item.get("admin_distance")
        h_description = h_item.get("description")
        h_vrf = h_item.get("vrf")
        h_afi = h_item.get("afi")
        h_addr = h_item.get("address")
        h_next_hop = h_item.get("next_hop").replace("null", "NULL")
        h_source = h_item.get("source_address")

        w_admin_dist = w_item.get("admin_distance")
        w_description = w_item.get("description")
        w_vrf = w_item.get("vrf")
        w_afi = w_item.get("afi")
        w_addr = self._get_address(w_item)
        w_next_hop = w_item.get("next_hop").replace("null", "NULL") if w_item.get("next_hop") else None
        w_source = w_item.get("source_address")

        # default sub-commands
        admin_dist_cmd = f" {h_admin_dist}" if h_admin_dist else ""
        description_cmd = f" description {h_description}" if h_description else ""
        h_vrf_cmd = f" vrf {h_vrf}" if h_vrf else ""  # used for deleting duplicate static routes
        vrf_cmd = f" vrf {h_vrf}" if h_vrf else ""
        source_cmd = f" {h_source}" if h_source and h_afi == "IPv6" else ""

        for c_item in diff:
            if c_item == "description":
                if w_description and w_description != h_description:
                    description_cmd = f" description {w_description}"
                    changed = True

                if deleted or replaced and not w_description and h_description:
                    description_cmd = ""
                    changed = True

            if c_item == "admin_distance":
                if w_admin_dist and w_admin_dist != h_admin_dist:
                    admin_dist_cmd = f" {w_admin_dist}"
                    changed = True

                if deleted or replaced and not w_admin_dist and h_admin_dist:
                    admin_dist_cmd = ""
                    changed = True

            if c_item == "vrf" and w_afi == "IPv4":
                if w_vrf and w_vrf != h_vrf:
                    vrf_cmd = f" vrf {w_vrf}"
                    changed = True

                if deleted or replaced and not w_vrf and h_vrf:
                    vrf_cmd = ""
                    changed = True

            if c_item == "source_address" and w_afi == "IPv6":
                if w_source and w_source != h_source:
                    source_cmd = f" {w_source}"
                    changed = True

                if deleted or replaced and not w_source and h_source:
                    source_cmd = ""
                    changed = True

        if changed or h_item.get('new'):
            afi_prefix = "ip" if w_afi == "IPv4" else w_afi.lower()
            commands.append(f"{afi_prefix} route{vrf_cmd} {w_addr}{source_cmd} {w_next_hop}{admin_dist_cmd}{description_cmd}")

            # need to remove the original static route if we are updating a route to remove the chance that
            # the cli adds a duplicate route instead of updating the existing route
            if not h_item.get("new"):
                commands.insert(0, f"no {afi_prefix} route{h_vrf_cmd} {h_addr} {h_source if h_source else ''} {h_next_hop}")

        return commands
