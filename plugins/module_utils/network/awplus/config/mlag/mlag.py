#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_mlag class
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
from ansible.module_utils.six import (
    iteritems
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts

parm_to_keyword = {'source_address': 'source-address',
                   'peer_address': 'peer-address',
                   'peer_link': 'peer-link',
                   'keepalive_interval': 'keepalive-interval',
                   'session_timeout': 'session-timeout'}

parm_to_default = {'source_address': None,
                   'peer_address': None,
                   'peer_link': None,
                   'keepalive_interval': 1,
                   'session_timeout': 30}

class Mlag(ConfigBase):
    """
    The awplus_mlag class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'mlag',
    ]

    def __init__(self, module):
        super(Mlag, self).__init__(module)
        self.domain_deleted = False

    def get_mlag_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        mlag_facts = facts['ansible_network_resources'].get('mlag')
        if not mlag_facts:
            return []
        return mlag_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        commands = list()

        existing_mlag_facts = self.get_mlag_facts()
        commands.extend(self.set_config(existing_mlag_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_mlag_facts = self.get_mlag_facts()
        result['before'] = existing_mlag_facts
        if result['changed']:
            result['after'] = changed_mlag_facts

        return result

    def set_config(self, existing_mlag_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_mlag_facts
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
        want = want if want else dict()
        have = have if have else dict()

        # Disallow empty config for non-override states as this would do nothing
        if want.get("domains") and len(want.get("domains")) < 1 and state in ('merged', 'replaced', 'deleted'):
            self._module.fail_json("At least one domain must be supplied.")

        # Temporarily enforce that only one domain is allowed at a time.
        if state in ('merged', 'replaced', 'overridden'):
            if want.get("domains") and len(want.get("domains")) > 1:
                self._module.fail_json("Currently only one domain is allowed at a time.")

        # Handle case with empty config when state is overridden early
        if not want.get("domains") and state == "overridden":
            for h_domain in have.get("domains"):
                commands.append(f"no mlag domain {h_domain.get("domain_id")}")
                return commands

        # Iterate through domains and delete domains that will need to be replaced
        # Eventually, once multiple domains are allowed, this will only apply to the overridden state.
        if state in ('merged', 'replaced', 'overridden'):
            for h_domain in have.get("domains"):
                keep = False
                for w_domain in want.get("domains"):
                    if h_domain.get("domain_id") == w_domain.get("domain_id"):
                        keep = True
                if not keep:
                    commands.append(f"no mlag domain {h_domain.get("domain_id")}")
                    self.domain_deleted = True

        # Iterate through each wanted domain and update their configs seperately
        for w_domain in want.get("domains"):
            h_match = {}
            for h_domain in have.get("domains"):
                if h_domain.get("domain_id") == w_domain.get("domain_id"):
                    h_match = h_domain

            if state == 'overridden':
                commands.extend(self._state_overridden(w_domain, h_match))
            elif state == 'deleted':
                commands.extend(self._state_deleted(w_domain, h_match))
            elif state == 'merged':
                commands.extend(self._state_merged(w_domain, h_match))
            elif state == 'replaced':
                commands.extend(self._state_replaced(w_domain, h_match))

        return commands

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        remove_dict = {}
        add_dict = {}
        domain_id = want.get("domain_id")
        for key, val in iteritems(want):
            if key == "domain_id":
                continue
            if val is not None and val != have.get(key, parm_to_default[key]):
                if val != parm_to_default[key]:
                    add_dict[key] = val
                else:
                    remove_dict[key] = val
        for key, val in iteritems(have):
            if key == "domain_id":
                continue
            if val != parm_to_default[key] and want.get(key) == parm_to_default[key]:
                remove_dict[key] = val

        commands.extend(self._update_partial(domain_id, add_dict, remove_dict))
        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        remove_dict = {}
        add_dict = {}
        domain_id = want.get("domain_id")
        for key, val in iteritems(have):
            if key == "domain_id":
                continue
            if val is not None and val != parm_to_default[key] and want.get(key) is None:
                remove_dict[key] = val
        for key, val in iteritems(want):
            if key == "domain_id":
                continue
            if val is not None and val != have.get(key, parm_to_default[key]):
                if val != parm_to_default[key]:
                    add_dict[key] = val
                else:
                    remove_dict[key] = val

        commands.extend(self._update_partial(domain_id, add_dict, remove_dict))
        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        remove_dict = {}
        add_dict = {}
        domain_id = want.get("domain_id")
        for key, val in iteritems(want):
            if key == "domain_id":
                continue
            if val is not None and val != have.get(key, parm_to_default[key]):
                if val != parm_to_default[key]:
                    add_dict[key] = val

        commands.extend(self._update_partial(domain_id, add_dict, remove_dict))
        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        remove_dict = {}
        remove_domain = True
        for key, val in iteritems(want):
            if key == "domain_id":
                continue
            if val != parm_to_default[key]:
                remove_domain = False
                if val is not None and have.get(key) != parm_to_default[key]:
                    remove_dict[key] = val

        domain_id = want.get("domain_id")
        if remove_domain:
            if domain_id == have.get("domain_id"):
                commands.append(f"no mlag domain {domain_id}")
        elif domain_id == have.get("domain_id"):
            commands.extend(self._update_partial(domain_id, {}, remove_dict))
        
        return commands

    def _update_partial(self, domain_id, add_dict, remove_dict):
        """
        Function for generating commands to partially update
        configuration from an existing domain based on dictionaries 
        which specify configuration to add and remove.
        
        :param domain_id: id of the domain to update
        :param add_dict: dictionary of config to add
        :param remove_dict: dictionary of config to remove
        :rtype: A list
        :returns: A list of commands to update the domain
        """
        commands = []
        for key, _ in iteritems(remove_dict):
            command = parm_to_keyword[key]
            commands.append(f"no {command}")
        for key, value in iteritems(add_dict):
            command = parm_to_keyword[key]
            commands.append(f"{command} {value}")

        if commands or self.domain_deleted:
            commands.insert(0, f"mlag domain {domain_id}")
        return commands
