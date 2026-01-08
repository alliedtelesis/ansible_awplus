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

        if state in ('merged', 'replaced', 'overridden'):
            have, domain_commands = self._delete_domain(want, have)
            commands.extend(domain_commands)

        if state == 'overridden':
            commands.extend(self._state_overridden(want, have))
        elif state == 'deleted':
            commands.extend(self._state_deleted(want, have))
        elif state == 'merged':
            commands.extend(self._state_merged(want, have))
        elif state == 'replaced':
            commands.extend(self._state_replaced(want, have))

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
        domain_id = want.get("domain")
        for key, val in iteritems(want):
            if key == "domain":
                continue
            if val is not None and val != have.get(key, parm_to_default[key]):
                if val != parm_to_default[key]:
                    add_dict[key] = val
                else:
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
        domain_id = want.get("domain")
        for key, val in iteritems(have):
            if key == "domain":
                continue
            if val is not None and val != parm_to_default[key] and want.get(key) is None:
                remove_dict[key] = val
        for key, val in iteritems(want):
            if key == "domain":
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
        domain_id = want.get("domain")
        for key, val in iteritems(want):
            if key == "domain":
                continue
            if val is not None and val != have.get(key, parm_to_default[key]):
                if val != parm_to_default[key]:
                    add_dict[key] = val
                else:
                    remove_dict[key] = val
        for key, val in iteritems(have):
            if key == "domain":
                continue
            if val is not None and val != parm_to_default[key] and want.get(key) is None:
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
        for key, val in iteritems(want):
            if key == "domain":
                continue
            if val is not None and val != parm_to_default[key]:
                remove_dict[key] = val

        domain_id = want.get("domain")
        if not remove_dict:
            if want.get("domain") == have.get("domain"):
                commands.append(f"no mlag domain {domain_id}")
        else:
            commands.extend(self._update_partial(domain_id, {}, remove_dict))
        
        return commands

    def _delete_domain(self, want, have):
        """
        Function for replacing the domain which
        requires its deletion
        
        :param want: want config dict
        :param have: have config dict
        """
        commands = []
        w_domain, h_domain = want.get("domain"), have.get("domain")
        if w_domain and h_domain and w_domain != h_domain:
            commands.append(f"no mlag domain {h_domain}")
            have = { "domain": w_domain }

        return have, commands

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

        if commands:
            commands.insert(0, f"mlag domain {domain_id}")

        return commands
