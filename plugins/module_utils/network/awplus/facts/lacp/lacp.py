#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus lacp fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.lacp.lacp import LacpArgs


class LacpFacts(object):
    """ The awplus lacp fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = LacpArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_lacp_config(self, connection):
        return connection.get('show lacp sys-id')
    
    def get_running_config(self, connection):
        return connection.get('show running-config')

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for lacp
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            # Normal situation should be no data. Since we need data
            # from multiple sources, it's probably best if we just ignore
            # any data passed in.
            pass

        # Get required information
        glc = self.get_lacp_config(connection)
        grc = self.get_running_config(connection)

        # split the config into instances of the resource. don't do it the way
        # the template suggests since we can't just conveniently split the data
        # into sections.
        config = deepcopy(self.generated_spec)

        # get list of controllers and ports and add to config.
        config = self.render_priority(config, glc)
        config = self.render_global_passive_mode(grc)

        config = utils.remove_empties(config)

        ansible_facts['ansible_network_resources'].pop('lacp', None)

        facts = {'lacp': config}
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    def render_priority(self, have, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param have: The new have config
        :param conf: The text output config
        :rtype: dictionary
        :returns: The generated config
        """
        # System Priority: 0x8000 (32768)
        match = re.search(r'System Priority: .+\((\d+)\)', conf)
        have['system']['priority'] = int(match.group(1))

        return have

    def render_global_passive_mode(self, spec, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)
        if re.search(r'lacp global-passive-mode enable', conf):
            config['system']['global_passive_mode'] = True
        else:
            config['system']['global_passive_mode'] = False

        return config
