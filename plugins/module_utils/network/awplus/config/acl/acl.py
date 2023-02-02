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
        # with open("output.txt", "a") as f:
        #     f.write(f"\nansible_facts {acl_facts}")
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
            f.write(f"")

        existing_acl_facts = self.get_acl_facts()
        # with open("output.txt", "a") as f:
        #     f.write(f"\nansible_facts: {existing_acl_facts}")
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
        # with open("output.txt", "a") as f:
        #     f.write(f"\nwant {want}")
        have = existing_acl_facts
        # with open("output.txt", "a") as f:
        # #     f.write(f"\nhave {have}")
        resp = self.set_state(want, have)
        return to_list(resp)
    
    def check_parameters(self, state, want):
        
        # want_acl = want[0].get('acls')[0]
        # want_ace = want_acl.get('aces')[0]
        # acl_type = want_acl.get('acl_type')
        for item in want:
            w_acls = item.get('acls')
            for w_acl in w_acls:
                w_aces = w_acl.get('aces') if w_acl.get('aces') is not None else []
                acl_type = w_acl.get('acl_type')
                for w_ace in w_aces:
                    # with open("output.txt", "a") as f:
                    #     f.write(f"\n {w_aces}")
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
                    if w_acl.get('name') is None:
                        self._module.fail_json(
                            msg=f"Missing acl parameter 'name' for state {state}"
                        )
        

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        state = self._module.params['state']
        # with open("output.txt", "a") as f:
        #     f.write(f"\n{want}")
        if state in ('merged', 'replaced', 'overridden'):
            self.check_parameters(state, want)

        
            


        # with open("output.txt", "a") as f:
        #     f.write(f"{want_acl}\nace{want_ace}")
           
        # if 
        #     self._module.fail_json(
        #         msg=f"value of config parameter must not be empty for state {state}")

        
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
        h_acls = have["acls"]
        for w_acls in want:
            for w_acl in w_acls.get('acls'):
                w_aces = w_acl.get('aces')
                with open("output.txt", "a") as f:
                    f.write(f"\nw_ace{w_aces}\n")
                for thing in h_acls:
                    if w_acl.get('name') == thing.get('name'):
                        commands.append(f"access-list {thing.get('name')}")
                        for h_ace in thing.get('ace'):
                            
                            commands.append(
                                f"no {h_ace.get('action')} {'' if h_ace.get('protocols') is None else h_ace.get('protocols')} "
                                f"{h_ace.get('source_addr')} {'' if h_ace.get('destination_addr') is None else h_ace.get('destination_addr')}"
                            )
                        for ace in w_aces:
                            commands.append(
                                f"{ace.get('action')} {'' if ace.get('protocols') is None else ace.get('protocols')} "
                                f"{ace.get('source_addr')} {'' if ace.get('destination_addr')is None else ace.get('destination_addr')}"
                            )
        # with open("output.txt", "a") as f:
        #     f.write(f"\n{commands}")
        return commands


        for thing in h_acls:
            if w_acls.get('name') == thing.get('name'):
                # with open("output.txt", "a") as f:
                #     f.write(f"\n{w_acls}")
                commands.append(f"access-list {thing.get('name')}")
                # with open("output.txt", "a") as f:
                #     f.write(f"\n{thing.get('ace')}")
                for h_ace in thing.get('ace'):
                    
                    commands.append(
                        f"no {h_ace.get('action')} {h_ace.get('protocols')} "
                        f"{h_ace.get('source_addr')} {h_ace.get('destination_addr')}"
                    )
                for ace in w_aces:
                    # with open("output.txt", "a") as f:
                        # f.write(f"\n{ace}")
                    commands.append(
                        f"{ace.get('action')} {ace.get('protocols')} "
                        f"{ace.get('source_addr')} {ace.get('destination_addr')}"
                    )

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
            h_acl_type = h_acl.get('type')
            if h_acl.get('name').isnumeric(): #numbered acl
                commands.append(f"no access-list {h_acl.get('name')}")
            else:
                h_afi = h_acl.get('afi')
                with open("output.txt", "a") as f:
                    f.write(f"\nh_acl {h_acl_type} {h_afi}")
                
                # cmd_type = 'hardware' if h_acl_type == 'Hardware' else 'extended'
                if h_afi == 'IPv4' or h_acl_type == 'Standard':
                    cmd_type = h_acl_type
                else:
                    cmd_type = ''
                commands.append(f"no {'' if h_afi == 'IPv4' else 'IPv6'} access-list {cmd_type} {h_acl.get('name')}")
        
        # adding new
        for item in want:
            w_acls = item.get('acls')
            w_afi = item.get('afi')
            for w_acl in w_acls:
                # with open("output.txt", "a") as f:
                #     f.write(f"\n{commands}")
                w_aces = w_acl.get('aces')
                if w_acl.get('acl_type') == 'hardware':
                    if len(w_aces) > 1:
                        self._module.fail_json(msg="only one ace allowed for hardware acls")
                    with open("output.txt", "a") as f:
                        f.write(f"\nthe one {w_aces}")
                    commands.append(
                        f"{'' if w_afi == 'IPv4' else 'IPv6'} access-list {w_acl.get('name')} {w_aces[0].get('action')} {w_aces[0].get('protocols')} "
                        f"{w_aces[0].get('source_addr')} {w_aces[0].get('destination_addr')}"
                    )
                else:    
                    commands.append(
                        f"{'' if w_afi == 'IPv4' else 'IPv6'} access-list {'extended' if not w_acl.get('name').isnumeric() else ''} {w_acl.get('name')}"
                    )
                
                    for ace in w_aces:
                        commands.append(
                            f"{ace.get('action')} {'' if ace.get('protocols') is None else ace.get('protocols')} "
                            f"{ace.get('source_addr')} {'' if ace.get('destination_addr') is None else ace.get('destination_addr')}"
                        )
        with open("output.txt", "a") as f:
            f.write(f"\n{commands}")


        return commands
    
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        h_acls = have["acls"]
        # w_acls = want[0]['acls'][0]
        # w_aces = w_acls.get('aces')
        


        for item in want:
            w_acls = item.get('acls')
            w_afi = item.get('afi')
            
            for w_acl in w_acls:
                existing_acl = False
                w_aces = w_acl.get('aces')
                
                # with open("output.txt", "a") as f:
                #     f.write(f"\n {w_acl}")
                w_acl_type = w_acl.get('acl_type')
                if not w_acl.get('name').isnumeric() and w_acl_type not in ('hardware', 'standard'):
                    cmd_type = 'extended'
                elif w_acl_type == 'hardware':
                    cmd_type = 'hardware'
                else:
                    cmd_type = ''
                with open("output.txt", "a") as f:
                            f.write(f"\n {w_acl}")
                for h_count, thing in enumerate(h_acls):
                    # with open("output.txt", "a") as f:
                    #     f.write(f"\n {thing}")
                    cmd = []
                    
                    if w_acl.get('name') == thing.get('name'): #an ace exists within the acl so modify the aces
                        existing_acl = True
                        
                        h_aces = thing.get('ace') if thing.get('ace') is not None else []
                        cmd.append(f"{'' if w_afi == 'IPv4' else 'IPv6'} access-list {cmd_type} {thing.get('name')}")
                        for ace in w_aces:
                            test = dict(ace) #need to rename test to something better ---------------------------------------------------------------
                            with open("output.txt", "a") as f:
                                f.write(f"\n here{w_acl_type}")
                            if "ace_ID" in test:
                                test.pop("ace_ID")
                            else:
                                self._module.fail_json(msg="'ace_ID' is required when merging aces")
                            if test not in h_aces:
                                cmd.append(
                                    f"{ace.get('ace_ID')} {ace.get('action')} "
                                    f"{'' if ace.get('protocols') is None else ace.get('protocols')} {ace.get('source_addr')} {'' if ace.get('destination_addr') is None else ace.get('destination_addr')}"
                                )
                    if len(cmd) > 1: # only add command if needed
                        commands.extend(cmd)
                if not existing_acl:
                    commands.append(f"{'' if w_afi == 'IPv4' else 'IPv6'} access-list {cmd_type} {w_acl.get('name')}")
                    for ace in w_aces:
                        commands.append(
                            f"{ace.get('action')} {'' if ace.get('protocols') is None else ace.get('protocols')} "
                            f"{ace.get('source_addr')} {'' if ace.get('destination_addr') is None else ace.get('destination_addr')}"
                        )
        with open("output.txt", "a") as f:
            f.write(f"\ncommands {commands}")
        return commands
        commands = []
        h_acls = have["acls"]
        w_acls = want[0]['acls'][0]
        w_aces = w_acls.get('aces')
        existing_acl = False
        for thing in h_acls:
            if w_acls.get('name') == thing.get('name'): #an ace exists within the acl so modify the aces
                existing_acl = True
                h_aces = thing.get('ace') if thing.get('ace') is not None else []
                w_aces = w_acls.get('aces')
                for ace in w_aces:
                    test = dict(ace) #need to rename test to something better ---------------------------------------------------------------
                    if "ace_ID" in test:
                        test.pop("ace_ID")
                    else:
                        self._module.fail_json(msg="'ace_ID' is required when merging aces")
                    if test not in h_aces:
                        commands.append(
                            f"{ace.get('ace_ID')} {ace.get('action')} "
                            f"{ace.get('protocols')} {ace.get('source_addr')} {ace.get('destination_addr')}"
                        )
                    if len(commands) != 0 and f"access-list {thing.get('name')}" not in commands:
                        commands.insert(0, f"access-list {thing.get('name')}")
        if not existing_acl:
            commands.append(f"access-list {w_acls.get('name')}")
            for ace in w_aces:
                commands.append(
                    f"{ace.get('action')} {ace.get('protocols')} "
                    f"{ace.get('source_addr')} {ace.get('destination_addr')}"
                )
    
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        # thing = self._module.params
        h_acls = have["acls"]
        # w_acls = want[0]['acls'][0]
        # w_aces = w_acls.get('aces')[0] if w_acls.get('aces') is not None else []
        # with open("output.txt", "a") as f:
        #     f.write(f"\nwant {want}\nh_acls {h_acls}")
        for item in want:
            # with open("output.txt", "a") as f:
            #     f.write(f"\nitem {item}")
            w_acls = item.get('acls')
            w_afi = item.get('afi')
            # with open("output.txt", "a") as f:
            #     f.write(f"\nafi {w_afi}")
            for w_acl in w_acls:
                w_aces = w_acl.get('aces')
                for thing in h_acls:
                    if w_acl.get('name') == thing.get('name'):
                        if w_aces is None: #delete the acl if no ace is provided
                            commands.append(
                                f"{'' if w_afi == 'IPv4' else 'IPv6'} no access-list {'extended' if not w_acl.get('name').isnumeric() else ''} {thing.get('name')}"
                            )
                        else: #delete the specified ace entry only
                            self.check_parameters('deleted', want)
                            commands.append(f"{'' if w_afi == 'IPv4' else 'IPv6'} access-list {'extended' if not w_acl.get('name').isnumeric() else ''} {thing.get('name')}")
                            for w_ace in w_aces:
                                for h_ace in thing.get('ace'):
                                    if h_ace == w_ace:
                                        commands.append(
                                            f"no {w_ace.get('action')} {w_ace.get('protocols')} {w_ace.get('source_addr')} {w_ace.get('destination_addr')}"
                                        )
            # with open("output.txt", "a") as f:
            #     f.write(f"\nthing {thing.get('ace')[0]}\n {w_aces}\n")





        # for h_acl in h_acls:
        #     h_acl_type = h_acl.get('type')
        #     if h_acl.get('name').isnumeric(): #numbered acl
        #         commands.append(f"no access-list {h_acl.get('name')}")
        #     else:
        #         h_afi = h_acl.get('afi')
        #         with open("output.txt", "a") as f:
        #             f.write(f"\nh_acl {h_acl_type} {h_afi}")
                
        #         # cmd_type = 'hardware' if h_acl_type == 'Hardware' else 'extended'
        #         if h_afi == 'IPv4' or h_acl_type == 'Standard':
        #             cmd_type = h_acl_type
        #         else:
        #             cmd_type = ''
        #         commands.append(f"no {'' if h_afi == 'IPv4' else 'IPv6'} access-list {cmd_type} {h_acl.get('name')}")


        with open("output.txt", "a") as f:
            f.write(f"\n{commands}")
        return commands


# eagles what kind of love have you got


#         commands = []
#         h_acls = have["acls"]
#         w_acls = want[0]['acls'][0]
#         w_aces = w_acls.get('aces')
#         existing_acl = False
#         with open("output.txt", "a") as f:
#             f.write(f"\n{w_aces}")
#         for thing in h_acls:
#             if w_acls.get('name') == thing.get('name'): #an ace exists within the acl so modify the ace
#                 existing_acl = True
#                 h_aces = thing.get('ace')[0] if thing.get('ace') is not None else []
#                 w_aces = w_acls.get('aces')

#                 test = dict(w_acls.get('aces')[0])
#                 if "ace_ID" in test:
#                     test.pop("ace_ID")
#                 else:
#                     self._module.fail_json(msg="'ace_ID' is required when merging aces")
#                 with open("output.txt", "a") as f:
#                             f.write(f"\nhere") 
#                 if test != h_aces: #checks if want ace and have ace match and generates the required commands to modify it
#                     with open("output.txt", "a") as f:
#                         f.write(f"\n{test}")
#                     commands.append(f"access-list {thing.get('name')}")
#                     # with open("output.txt", "a") as f:
#                     #         f.write(f"\nhere") 
#                     for ace in w_aces:
#                         # with open("output.txt", "a") as f:
#                         #     f.write(f"ace {ace}\n h_aces{h_aces}\n")
#                         commands.append(
#                             f"{ace.get('ace_ID')} {ace.get('action')} "
#                             f"{ace.get('protocols')} {ace.get('source_addr')} {ace.get('destination_addr')}"
#                         )
#                         with open("output.txt", "a") as f:
#                             f.write(f"\nhere") 
#         if not existing_acl:
#             ace = w_aces[0]
#             commands.append(
#                 f"access-list {w_acls.get('name')} {ace.get('action')} "
#                 f"{ace.get('protocols')} {ace.get('source_addr')} {ace.get('destination_addr')}"
#             )
#         #     with open("output.txt", "a") as f:
#         #         f.write(f"\n {w_aces}")
#         with open("output.txt", "a") as f:
#             f.write(f"\n {commands}")
#         return []




# awplus#show access-list 
# Standard IP access list 72
#     4 deny   168.152.66.0 0.0.0.255
# Extended IP access list 102
#     4 permit ip 172.144.44.0 0.0.0.255 any
# Extended IP access list 103
#     4 permit ip 196.148.88.0 0.0.0.255 any
#     8 deny   ip 198.146.98.0 0.0.0.255 any
# Extended IP access list 104
#     8 permit ip 196.144.88.0 0.0.0.255 any
# Extended IP access list 2001
# Named Extended IP access list test
#     4 permit ip 192.143.87.0/24 192.142.50.0/24
# Named Extended IP access list test2
#     4 permit icmp 148.148.48.0/24 152.152.52.0/24
#     8 deny   icmp 142.141.40.0/24 132.131.30.0/24 icmp-type 8
# Named Extended IPv6 access list a-list
#     4 deny   icmp 2001:db8::/64 2001:db8::f/64
#     8 deny   icmp 2001:db8::/64 2001:db8::d/64 icmp-type 8
# Hardware IP access list 3000
#     4 permit ip 192.121.1.1/24 any
