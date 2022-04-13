#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_ntp class
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
    remove_empties,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.facts.facts import Facts


class Ntp(ConfigBase):
    """
    The awplus_ntp class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'ntp',
    ]

    def __init__(self, module):
        super(Ntp, self).__init__(module)

    def get_ntp_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        ntp_facts = facts['ansible_network_resources'].get('ntp')
        if not ntp_facts:
            return {}
        return ntp_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_ntp_facts = self.get_ntp_facts()
        commands.extend(self.set_config(existing_ntp_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_ntp_facts = self.get_ntp_facts()

        result['before'] = existing_ntp_facts
        if result['changed']:
            result['after'] = changed_ntp_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_ntp_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_ntp_facts
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
        kwargs = {'self': self, 'want': want, 'have': have}

        if state == 'overridden':
            commands = self._state_overridden(**kwargs)
        elif state == 'deleted':
            commands = self._state_deleted(**kwargs)
        elif state == 'merged':
            commands = self._state_merged(**kwargs)
        elif state == 'replaced':
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
        if want.get('server'):
            for each in have.get('server', []):
                if each not in want['server']:
                    commands.extend(_clear_server(each))
        if want.get('authentication'):
            for each in have.get('authentication', []):
                if each not in want['authentication']:
                    commands.extend(_clear_auth(each))
        if want.get('source'):
            if want['source'] != have.get('source'):
                commands.extend(_clear_source('source'))

        commands.extend(self._state_merged(self, want, have))

        return commands

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        want = remove_empties(want)
        if have.get('server'):
            for each in have['server']:
                if each not in want.get('server', []):
                    commands.extend(_clear_server(each))
        if have.get('authentication'):
            for each in have['authentication']:
                if each not in want.get('authentication', []):
                    commands.extend(_clear_auth(each))
        if have.get('source_int') and have.get('source_int') != want.get('source_int'):
            commands.extend(_clear_source('source'))

        commands.extend(self._state_merged(self, want, have))

        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        if want.get('server'):
            for each in want['server']:
                if each not in have.get('server', []):
                    commands.extend(_set_server(each))
        if want.get('authentication'):
            for each in want['authentication']:
                if not is_key_in_have(each['key_id'], have.get('authentication', [])):
                    commands.extend(_set_auth(each))
        if want.get('source_int') and want.get('source_int') != have.get('source_int', ''):
            commands.extend(_set_source(want['source_int']))

        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        if want:
            if want.get('server'):
                for each in want['server']:
                    if each in have.get('server', []):
                        commands.extend(_clear_server(each))
            if want.get('authentication'):
                for each in want['authentication']:
                    if is_key_in_have(each['key_id'], have.get('authentication', [])):
                        commands.extend(_clear_auth(each))
            if want.get('source_int') == have.get('source_int'):
                commands.extend(_clear_source(want['source_int']))
        else:
            if have.get('server'):
                for each in have['server']:
                    commands.extend(_clear_server(each))
            if have.get('authentication'):
                for each in have['authentication']:
                    commands.extend(_clear_auth(each))
            if have.get('source_int'):
                commands.extend(_clear_source(have['source_int']))

        return commands


def _set_server(server):
    commands = []
    commands.append('ntp server {}'.format(server))
    return commands


def _set_source(source):
    commands = []
    commands.append('ntp source {}'.format(source))
    return commands


def _set_auth(want):
    commands = []
    commands.append('ntp authentication-key {} {} {}'.format(want['key_id'], want['key_type'], want['auth_key']))
    return commands


def _clear_server(server):
    commands = []
    commands.append('no ntp server {}'.format(server))
    return commands


def _clear_source(source):
    commands = []
    commands.append('no ntp source')
    return commands


def _clear_auth(want):
    commands = []
    commands.append('no ntp authentication-key {}'.format(want['key_id']))
    return commands


def is_key_in_have(key_id, have):
    for each in have:
        if each['key_id'] == key_id:
            return True
    return False
