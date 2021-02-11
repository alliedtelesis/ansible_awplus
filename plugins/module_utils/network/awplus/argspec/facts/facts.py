#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The arg spec for the awplus facts module.
"""


class FactsArgs(object):  # pylint: disable=R0903
    """ The arg spec for the awplus facts module
    """

    def __init__(self, **kwargs):
        pass

    choices = [
        'all',
        'banner',
        'bgp',
        'interfaces',
        'l2_interfaces',
        'l3_interfaces',
        'lacp',
        'lacp_interfaces',
        'lag_interfaces',
        'lldp_global',
        'lldp_interfaces',
        'logging',
        'ntp',
        'static_lag_interfaces',
        'user',
        'vlans',
        'vrfs',
    ]

    argument_spec = {
        'gather_subset': dict(default=['!config'], type='list'),
        'gather_network_resources': dict(choices=choices,
                                         type='list'),
    }
