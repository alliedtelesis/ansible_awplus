#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus_logging class
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


class Logging(ConfigBase):
    """
    The awplus_logging class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'logging',
    ]

    def __init__(self, module):
        super(Logging, self).__init__(module)

    def get_logging_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        logging_facts = facts['ansible_network_resources'].get('logging')
        if not logging_facts:
            return []
        return logging_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_logging_facts = self.get_logging_facts()
        commands.extend(self.set_config(existing_logging_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_logging_facts = self.get_logging_facts()

        result['before'] = existing_logging_facts
        if result['changed']:
            result['after'] = changed_logging_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_logging_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_logging_facts
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
        wants = []
        dests = []
        for each in want:
            validate_input(each, self._module)
            each = remove_empties(each)
            wants.append(each)
            if each['dest'] == 'host':
                host_dict = get_host(each)
                wants.append(host_dict)
                dests.append(each['name'])
            else:
                dests.append(each['dest'])
            if each not in have:
                if each.get('size'):
                    commands.extend(_set_size_conf(each))
                if each['dest'] == 'host':
                    if host_dict not in have:
                        commands.extend(_set_levfac_conf(host_dict))
                if each.get('level') or each.get('facility'):
                    commands.extend(_set_levfac_conf(each))

        for each in have:
            if (each['dest'] in dests or each.get('name') in dests) and each not in wants:
                if each['dest'] == 'host':
                    if get_host(each) in wants:
                        commands.extend(_clear_levfac_conf(each))
                    elif not (each.get('level') or each.get('facility')):
                        commands.extend(_clear_levfac_conf(get_host(each)))
                elif each.get('size'):
                    commands.extend(_clear_size_conf(each))
                elif each.get('level') or each.get('facility'):
                    commands.extend(_clear_levfac_conf(each))

        return commands

    @staticmethod
    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        wants = []
        for each in want:
            validate_input(each, self._module)
            each = remove_empties(each)
            wants.append(each)
            if each['dest'] == 'host':
                host_dict = get_host(each)
                wants.append(host_dict)
            if each not in have:
                if each.get('size'):
                    commands.extend(_set_size_conf(each))
                if each['dest'] == 'host':
                    if host_dict not in have:
                        commands.extend(_set_levfac_conf(host_dict))
                if each.get('level') or each.get('facility'):
                    commands.extend(_set_levfac_conf(each))

        for each in have:
            if each not in wants:
                if each['dest'] == 'host':
                    if get_host(each) in wants:
                        commands.extend(_clear_levfac_conf(each))
                    elif not (each.get('level') or each.get('facility')):
                        commands.extend(_clear_levfac_conf(get_host(each)))
                elif each.get('size'):
                    commands.extend(_clear_size_conf(each))
                elif each.get('level') or each.get('facility'):
                    commands.extend(_clear_levfac_conf(each))

        return commands

    @staticmethod
    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        for each in want:
            validate_input(each, self._module)
            if remove_empties(each) not in have:
                if each.get('size'):
                    commands.extend(_set_size_conf(each))
                if each['dest'] == 'host':
                    host_dict = get_host(each)
                    if host_dict not in have:
                        commands.extend(_set_levfac_conf(host_dict))
                if each.get('level') or each.get('facility'):
                    commands.extend(_set_levfac_conf(each))

        return commands

    @staticmethod
    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        if not want:
            for each in have:
                if each['dest'] == 'host':
                    if not (each.get('level') or each.get('facility')):
                        commands.extend(_clear_levfac_conf(each))
                elif each.get('size'):
                    commands.extend(_clear_size_conf(each))
                elif each.get('level') or each.get('facility'):
                    commands.extend(_clear_levfac_conf(each))
        else:
            for each in want:
                if remove_empties(each) in have:
                    if each.get('size'):
                        commands.extend(_clear_size_conf(each))
                    elif each.get('level') or each.get('facility'):
                        commands.extend(_clear_levfac_conf(each))
                    elif each['dest'] == 'host':
                        commands.extend(_clear_levfac_conf(each))

        return commands


def _set_size_conf(want):
    commands = []
    commands.append('log {} size {}'.format(want['dest'], want['size']))
    return commands


def _set_levfac_conf(want):
    commands = []
    dest = ' {}'.format(want['dest']) if want['dest'] != 'facility' else ''
    host = ' {}'.format(want['name']) if want['dest'] == 'host' else ''
    level = ' level {}'.format(want['level']) if want.get('level') else ''
    facility = ' facility {}'.format(want['facility']) if want.get('facility') else ''
    command = 'log{}{}{}{}'.format(dest, host, level, facility)
    commands.append(command)
    return commands


def _clear_size_conf(have):
    commands = []
    commands.append('no log {} size'.format(have['dest']))
    return commands


def _clear_levfac_conf(have):
    commands = []
    dest = ' {}'.format(have['dest'])
    host = ' {}'.format(have['name']) if have['dest'] == 'host' else ''
    level = ' level {}'.format(have['level']) if have.get('level') else ''
    facility = ' facility {}'.format(have['facility']) if have.get('facility') and have['dest'] != 'facility' else ''
    command = 'no log{}{}{}{}'.format(dest, host, level, facility)
    commands.append(command)
    return commands


def validate_input(want, module):
    # if not (want.get('size') or want.get('level') or want.get('facility')):
    #     module.fail_json(msg='One of size, level and facility is required.')
    if want.get('size') and (want.get('level') or want.get('facility')):
        module.fail_json(msg='size is mutually exclusive to level and facility.')
    if want['dest'] == 'host' and not want.get('name'):
        module.fail_json(msg='name is required when dest = host')
    if want['dest'] == 'facility' and not want.get('facility'):
        module.fail_json(msg='facility is required when dest = facility')
    if want.get('size') and want['dest'] not in ('buffered', 'external', 'permanent'):
        module.fail_json(msg='size cannot be configured when dest = {}'.format(want['dest']))
    if want['dest'] == 'facility' and want.get('level'):
        module.fail_json(msg='level connot be configured when dest = facility')


def get_host(want):
    host_dict = {
        'dest': 'host',
        'name': want['name'],
    }
    return host_dict
