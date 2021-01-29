#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_vrfs class
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


class Vrfs(ConfigBase):
    """
    The awplus_vrfs class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'vrfs',
    ]

    def __init__(self, module):
        super(Vrfs, self).__init__(module)
        self.want_name_by_id = None
        self.want_id_by_name = None
        self.have_name_by_id = None
        self.have_id_by_name = None

    def get_vrfs_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        vrfs_facts = facts['ansible_network_resources'].get('vrfs')
        if not vrfs_facts:
            return []
        return vrfs_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_vrfs_facts = self.get_vrfs_facts()
        commands.extend(self.set_config(existing_vrfs_facts))
        if commands:
            if not self._module.check_mode:
                warning = self._connection.edit_config(commands).get("response")
                for warn in warning:
                    if warn != "":
                        warnings.append(warn)
            result['changed'] = True
        result['commands'] = commands

        changed_vrfs_facts = self.get_vrfs_facts()

        result['before'] = existing_vrfs_facts
        if result['changed']:
            result['after'] = changed_vrfs_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_vrfs_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_vrfs_facts
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
        if not self.check_vrf_name_id(have, want, False):
            self._module.fail_json(msg="failed name/id checks")
            return commands

        # delete all VRFs that appear in want
        for vname in self.want_id_by_name:
            commands.append('no ip vrf {}'.format(vname))

        # add all wanted VRFs
        for vname in self.want_id_by_name:
            commands.extend(self.config_one_vrf(want, vname, True))
        return commands

    def _state_overridden(self, have, want):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        if not self.check_vrf_name_id(have, want, True):
            self._module.fail_json(msg="failed name/id checks")
            return commands

        # delete all existing VRFs
        for vname in self.have_id_by_name:
            commands.append('no ip vrf {}'.format(vname))

        # add all wanted VRFs
        for vname in self.want_id_by_name:
            commands.extend(self.config_one_vrf(want, vname, True))
        return commands

    def _state_merged(self, have, want):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        if not self.check_vrf_name_id(have, want, False):
            self._module.fail_json(msg="failed name/id checks")
            return commands

        # deal with merging and rd change
        commands.extend(self.merge_rd_check(have, want))

        # deal with merging and route_target changes
        commands.extend(self.merge_route_target_check(have, want))

        # add all wanted VRFs
        for vname in self.want_id_by_name:
            commands.extend(self.config_one_vrf(want, vname, True))
        return commands

    def _state_deleted(self, have, want):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        if not self.check_vrf_name_id(have, want, False):
            self._module.fail_json(msg="failed name/id checks")
            return commands

        for vname in self.want_id_by_name:
            if vname in self.have_id_by_name:
                commands.append("no ip vrf {}".format(vname))
        return commands

    def check_vrf_name_id(self, have, want, override):
        ''' Checks on VRF name and ID:
        - name and ID must both be defined in wants
        - can't have multiple VRFs in want with same name or ID
        - if not override, name in want which appears in have should match ID
        - if not override, ID in want which appears in have should match name
        While we are doing this, create a dictionary of rd have and want by name for
        later merge processing.
        :param: have: config device already has
        :param: want: config we want on device
        :param: override: True if operation is override (not merge or replace)
        :rtype: bool
        :returns: False if an error is found. as a side-effect, dictionaries created
                  in this routine are added to have, want.
        '''
        want_name_by_id = {}
        want_id_by_name = {}
        want_rd_by_name = {}
        if want is not None:
            for vrf in want:
                if 'name' not in vrf or 'id' not in vrf:
                    return False
                vname = vrf['name']
                vid = vrf['id']
                if vname in want_id_by_name or vid in want_name_by_id:
                    return False
                want_id_by_name[vname] = vid
                want_name_by_id[vid] = vname
                want_rd_by_name[vname] = vrf.get('rd')
        have_name_by_id = {}
        have_id_by_name = {}
        have_rd_by_name = {}
        for vrf in have:
            if 'name' not in vrf or 'id' not in vrf:
                return False
            vname = vrf['name']
            vid = vrf['id']
            if vname in have_id_by_name or vid in have_name_by_id:
                return False
            have_id_by_name[vname] = vid
            have_name_by_id[vid] = vname
            have_rd_by_name[vname] = vrf.get('rd')
        if override:
            self.want_name_by_id = want_name_by_id
            self.want_id_by_name = want_id_by_name
            self.want_rd_by_name = want_rd_by_name
            self.have_name_by_id = have_name_by_id
            self.have_id_by_name = have_id_by_name
            self.have_rd_by_name = have_rd_by_name
            return True
        for vname in want_id_by_name:
            if vname in have_id_by_name:
                if want_id_by_name[vname] != have_id_by_name[vname]:
                    return False
        for vid in want_name_by_id:
            if vid in have_name_by_id:
                if want_name_by_id[vid] != have_name_by_id[vid]:
                    return False
        self.want_name_by_id = want_name_by_id
        self.want_id_by_name = want_id_by_name
        self.want_rd_by_name = want_rd_by_name
        self.have_name_by_id = have_name_by_id
        self.have_id_by_name = have_id_by_name
        self.have_rd_by_name = have_rd_by_name
        return True

    def config_one_vrf(self, want, vname, do_rd):
        ''' Create commands to configure a VRF from the list of VRFs
        in want whose name matches vname.
        :param: want: the list of want config items
        :param: vname: the name of the VRF to be configured
        :param: do_rd: special case - do we configure rd?
        :rtype: list
        :returns: None if something goes wrong, otherwise a list of commadns
                  to configure this VRF
        '''
        cmds = []
        first = True
        for vrf in want:
            if 'name' not in vrf or 'id' not in vrf or vrf['name'] != vname:
                continue
            if vname not in self.have_id_by_name:
                if first:
                    cmds.append("ip vrf {} {}".format(vname, vrf['id']))
                    first = False

            for attr, cmd_attr in [('description', 'description'),
                                   ('router_id', 'router-id'),
                                   ('max_static_routes', 'max-static-routes'),
                                   ('import_map', 'import map'),
                                   ('export_map', 'export map'), ]:
                if vrf.get(attr):
                    if first:
                        cmds.append("ip vrf {} {}".format(vname, vrf['id']))
                        first = False
                    cmds.append(" {} {}".format(cmd_attr, vrf.get(attr)))

            # max_fib_routes is special case
            if vrf.get('max_fib_routes'):
                if first:
                    cmds.append("ip vrf {} {}".format(vname, vrf['id']))
                    first = False
                if vrf.get('max_fib_routes_warning'):
                    cmds.append(" max-fib-routes {} {}".format(vrf.get('max_fib_routes'), vrf.get('max_fib_routes_warning')))
                else:
                    cmds.append(" max-fib-routes {}".format(vrf.get('max_fib_routes')))

            # rd is special case
            if do_rd and vrf.get('rd'):
                if first:
                    cmds.append("ip vrf {} {}".format(vname, vrf['id']))
                    first = False
                cmds.append(" rd {}".format(vrf.get('rd')))

            # route_target is a special case, it is a list
            if vrf.get('route_target'):
                for rt in vrf.get('route_target'):
                    if rt.get('target') and rt.get('direction'):
                        if first:
                            cmds.append("ip vrf {} {}".format(vname, vrf['id']))
                            first = False
                        cmds.append(" route-target {} {}".format(rt.get('direction'), rt.get('target')))
            break
        return cmds

    def merge_rd_check(self, have, want):
        ''' One of the vagaries of the ip vrf commands is that the rd cannot be changed.
        But from the Ansible abstraction point of view, it should be possible to make
        this change. The only way to do it is to delete the vrf, then add it again with
        the same parameters apart from rd.
        :param: have: the existing configuration
        :param: want: required configuration
        :returns: list of commands needed to make adjustments.
        '''
        cmds = []
        for vname in self.want_rd_by_name:
            have_rd = self.have_rd_by_name[vname] if vname in self.have_rd_by_name else None
            want_rd = self.want_rd_by_name[vname]
            if want_rd and have_rd and have_rd != want_rd:
                cmds.append("no ip vrf {}".format(vname))
                old_cmds = self.config_one_vrf(have, vname, False)
                if old_cmds:
                    cmds.extend(old_cmds)
        return cmds

    def merge_route_target_check(self, have, want):
        ''' Handle route_target changes. We want the result of merge to be the route-target
        specified in want, but we can't just override, because what will happen is the new
        config will merge with the old. That is we want (have:import, want:export) to result
        in export, not both. This means we have to remove the old route target, but this can
        only happen by referencing the current direction.
        :param: have: the existing configuration
        :param: want: required configuration
        :returns: list of commands needed to make adjustments.
        '''
        cmds = []
        if not want:
            return cmds
        for vrf in want:
            if 'route_target' not in vrf or vrf['route_target'] is None:
                continue
            for h_vrf in have:
                if h_vrf.get('name') == vrf.get('name'):
                    if 'route_target' in h_vrf and h_vrf['route_target'] is not None:
                        cmds.extend(self.rt_cmds(h_vrf, vrf))
        return cmds

    def rt_cmds(self, h_vrf, w_vrf):
        ''' Generate commands to undo required route_target entries. Assume that 'route_target' is
        present in both dictionaries, and that the name and id match.
        param: h_vrf: the have vrf - h_vrf['route_target'] is guaranteed to be iterable
        param: w_vrf: the want vrf - w_vrf['route_target'] is guaranteed to be iterable
        :rtype: list
        :returns: list of commands to remove relevant route targets
        '''
        cmds = []
        first = True
        for rt in w_vrf['route_target']:
            for h_rt in h_vrf['route_target']:
                if rt.get('target') == h_rt['target']:
                    if first:
                        cmds.append("ip vrf {} {}".format(h_vrf['name'], h_vrf['id']))
                        first = False
                    cmds.append(" no route-target {} {}".format(h_rt['direction'], h_rt['target']))
        return cmds
