#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus lldp_global fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.lldp_global.lldp_global import Lldp_globalArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.utils.utils import get_lldp_defaults


class Lldp_globalFacts(object):
    """ The awplus lldp_global fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Lldp_globalArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_device_data(self, connection):
        return connection.get('show running-config lldp')

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for lldp_global
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            # typically data is populated from the current device configuration
            data = self.get_device_data(connection)

        objs = {}
        if data:
            obj = self.render_config(self.generated_spec, data)
            if obj:
                objs = obj

        ansible_facts['ansible_network_resources'].pop('lldp_global', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['lldp_global'] = utils.remove_empties(params['config'])

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)

        multiplier = re.search(r'lldp holdtime-multiplier (\d+)', conf, re.M)
        if multiplier:
            config['holdtime_multiplier'] = multiplier.group(1)

        notif_int = re.search(r'lldp notification-interval (\d+)', conf, re.M)
        if notif_int:
            config['notification_interval'] = notif_int.group(1)

        reinit = re.search(r'lldp reinit (\d+)', conf, re.M)
        if reinit:
            config['reinit'] = reinit.group(1)

        timer = re.search(r'lldp timer (\d+)', conf, re.M)
        if timer:
            config['timer'] = timer.group(1)

        tx_delay = re.search(r'lldp tx-delay (\d+)', conf, re.M)
        if tx_delay:
            config['tx_delay'] = tx_delay.group(1)

        port_type = re.search(r'lldp port-number-type (\S+)', conf, re.M)
        if port_type:
            config['port_number_type'] = port_type.group(1)

        faststart_count = re.search(r'lldp faststart-count (\d+)', conf, re.M)
        if faststart_count:
            config['faststart_count'] = faststart_count.group(1)

        non_strict_check = re.search(r'lldp non-strict-med-tlv-order-check', conf, re.M)
        if non_strict_check:
            config['non_strict_med_tlv_order_check'] = True

        enabled = re.search(r'lldp run', conf, re.M)
        if enabled:
            config['enabled'] = True

        defaults = get_lldp_defaults()
        for key, value in utils.iteritems(config):
            if not value:
                config[key] = defaults[key]

        return utils.remove_empties(config)
