#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################

"""
The arg spec for the awplus_class_maps module
"""


class Class_mapsArgs(object):  # pylint: disable=R0903
    """The arg spec for the awplus_class_maps module
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {'config': {'elements': 'dict',
                     'options': {'access_group': {'type': 'str'},
                                 'cos': {'type': 'int'},
                                 'dscp': {'type': 'int'},
                                 'eth_format': {'choices': ['802dot2-tagged',
                                                            '802dot2-untagged',
                                                            'ethii-any',
                                                            'ethii-tagged',
                                                            'ethii-untagged',
                                                            'netwareraw-tagged',
                                                            'netwareraw-untagged',
                                                            'snap-tagged',
                                                            'snap-untagged'],
                                                'type': 'str'},
                                 'eth_protocol': {'type': 'str'},
                                 'inner_cos': {'type': 'int'},
                                 'inner_vlan': {'type': 'int'},
                                 'ip_precedence': {'type': 'int'},
                                 'mac_type': {'choices': ['l2bcast',
                                                          'l2mcast',
                                                          'l2ucast'],
                                              'type': 'str'},
                                 'name': {'required': True, 'type': 'str'},
                                 'tcp_flags': {'options': {'ack': {'type': 'bool'},
                                                           'fin': {'type': 'bool'},
                                                           'psh': {'type': 'bool'},
                                                           'rst': {'type': 'bool'},
                                                           'syn': {'type': 'bool'},
                                                           'urg': {'type': 'bool'}},
                                               'type': 'dict'},
                                 'vlan': {'type': 'int'}},
                                'required_together': ['eth_format', 'eth_protocol'],
                                'type': 'list'},
                     'state': {'choices': ['merged', 'replaced', 'overridden', 'deleted'],
                               'default': 'merged',
                               'type': 'str'}}  # pylint: disable=C0301
