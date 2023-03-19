#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus policy_maps fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.policy_maps.policy_maps import Policy_mapsArgs


class Policy_mapsFacts(object):
    """ The awplus policy_maps fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Policy_mapsArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    @staticmethod
    def get_policy_map_conf(connection):
        return connection.get("show policy-map")

    @staticmethod
    def get_policy_class_map_conf(connection):
        return connection.get("show running-config | begin policy-map")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for policy_maps
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if connection:  # just for linting purposes, remove
            pass

        if not data:
            # typically data is populated from the current device configuration
            # data = connection.get('show running-config | section ^interface')
            # using mock data instead
            data = self.get_policy_map_conf(connection)
            class_data = self.get_policy_class_map_conf(connection)

        # split the config into instances of the resource
        data = re.split(r'POLICY-MAP-NAME:', data)
        class_data = class_data.split('!')

        objs = []
        for resource in data:
            if resource:
                obj = self.render_config(self.generated_spec, resource, class_data)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('policy_maps', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['policy_maps'] = params['config']

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf, class_data):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)
        result = re.split(r'CLASS-MAP-NAME:', conf)
        if result:
            policy_conf = result[0].split('\n')

            # policy config
            config['name'] = policy_conf[0].lstrip()
            for item in result:
                default_action_match = re.search(r'Default class-map action: (\S+)', item)
                if default_action_match:
                    default_action = default_action_match.group(1)
                    default_action = default_action.replace('-', '_')
                    config['default_action'] = default_action

                description_match = re.search(r'Description: (.+)', item)
                if description_match:
                    config['description'] = description_match.group(1)

                trust_dscp_match = re.search(r'Trust state: (\S+)', item)
                if trust_dscp_match:
                    config['trust_dscp'] = True if trust_dscp_match.group(1) == 'DSCP' else False
            # get class config
            config['classifiers'] = self.render_classifiers(config.get('name'), class_data)
            config = utils.remove_empties(config)
        return config

    def render_classifiers(self, name, conf):
        """
        Render config for classifiers

        :param name: The name of the policy map
        :param conf: The class configuration of each policy map
        :rtype: list
        :returns: The classifier config for the policy-map
        """
        results = []
        policer = dict()
        remark_maps = []

        for classifier in conf:

            pol_name_match = re.search(r'policy-map (\S+)', classifier)
            if pol_name_match:
                # need to make sure name obtained matches the policy name obtained from parent function
                if pol_name_match.group(1) == name:
                    result = dict()
                    for item in classifier.split('\n'):

                        # class name
                        class_name_match = re.search(r'^ class (\S+)', item)
                        if class_name_match:
                            # append classifier to results and clear variables for next classifier
                            if result:
                                results.append(result)
                                result = dict()
                                remark_map = dict()
                                remark_maps = []
                                policer = dict()
                            result['name'] = class_name_match.group(1)

                        # policer facts
                        policer_match = re.match(r'  police (single-rate|twin-rate) (.+) action (\S+)', item)
                        if policer_match:
                            policer['type'] = policer_match.group(1).replace('-', '_')
                            policer['action'] = policer_match.group(3).replace('-', '_')
                            rate_type = policer_match.group(2)
                            if policer['type'] == 'single_rate':
                                sr_match = re.search(r'(\d+) (\d+) (\d+)', rate_type)
                                if sr_match:
                                    policer['cir'] = sr_match.group(1)
                                    policer['cbs'] = sr_match.group(2)
                                    policer['ebs'] = sr_match.group(3)
                            elif policer['type'] == 'twin_rate':
                                tr_match = re.search(r'(\d+) (\d+) (\d+) (\d+)', rate_type)
                                if tr_match:
                                    policer['cir'] = tr_match.group(1)
                                    policer['pir'] = tr_match.group(2)
                                    policer['cbs'] = tr_match.group(3)
                                    policer['pbs'] = tr_match.group(4)

                        # remark_map facts
                        remark_map_match = re.search(r'remark-map bandwidth-class (\S+) to new-dscp (\d+) new-bandwidth-class (\S+)', item)
                        if remark_map_match:
                            remark_map = {}
                            remark_map['class_in'] = remark_map_match.group(1)
                            remark_map['new_dscp'] = remark_map_match.group(2)
                            remark_map['new_class'] = remark_map_match.group(3)
                            remark_maps.append(remark_map)

                        # remark facts
                        remark_new_cos_match = re.search(r'remark new-cos (\d+) (\S+)', item)
                        if remark_new_cos_match:
                            result['remark'] = {'new_cos': remark_new_cos_match.group(1), 'apply': remark_new_cos_match.group(2)}

                        # pbr_next_hop facts
                        ip_next_hop_match = re.search(r'set ip next-hop (\S+)', item)
                        if ip_next_hop_match:
                            result['pbr_next_hop'] = ip_next_hop_match.group(1)

                        # storm facts
                        storm_protection_match = re.search(r'storm-protection', item)
                        if storm_protection_match:
                            result['storm_protection'] = True

                        storm_action_match = re.search(r'storm-action (\S+)', item)
                        if storm_action_match:
                            action = storm_action_match.group(1)
                            action = action.replace('disable', '_disable')
                            action = action.replace('down', '_down')
                            result['storm_action'] = action

                        storm_window_match = re.search(r'storm-window (\S+)', item)
                        if storm_window_match:
                            result['storm_window'] = storm_window_match.group(1)

                        storm_rate_match = re.search(r'storm-rate (\S+)', item)
                        if storm_rate_match:
                            result['storm_rate'] = storm_rate_match.group(1)

                        storm_downtime_match = re.search(r'storm-downtime (\S+)', item)
                        if storm_downtime_match:
                            result['storm_downtime'] = storm_downtime_match.group(1)

                        if policer:
                            result['policer'] = policer
                        if remark_maps:
                            result['remark_map'] = remark_maps

                    # append the last classifier to results
                    results.append(result)
        return results
