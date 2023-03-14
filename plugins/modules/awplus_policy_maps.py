#!/usr/bin/python
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
The module file for awplus_policy_maps
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'network'
}

DOCUMENTATION = """
---
module: awplus_policy_maps
version_added: 2.9
short_description: Manage policy maps on Allied Telesis AlliedWare Plus devices.
description: This module manages properties of policy maps on Allied Telesis AlliedWare Plus devices.
author: Tony van der Peet
notes:
- Tested against AlliedWare Plus on SBx908NG and x930.
options:
  config:
    description: A list of policy map configurations.
    type: list
    elements: dict
    suboptions:
      name:
        description:
        - ID of the policy-map, an arbitrary string.
        type: str
        required: True
      description:
        description:
        - A human readable description of the policy-map.
        type: str
      default_action:
        description:
        - The action applied to the default classifier map for this policy.
        type: str
        choices:
        - permit
        - deny
        - copy_to_cpu
        - send_to_cpu
        - copy_to_mirror
        - send_to_mirror
        default: permit
      trust_dscp:
        description:
        - Whether to enable the premark-dscp to replace the DSCP, bandwidth class and/or CoS based on a lookup DSCP value.
        type: bool
        default: false
      classifiers:
        description:
        - Classifiers to apply to this policy map.
        type: list
        elements: dict
        suboptions:
          name:
            description:
            - The name of this classifier, either "default" or the name of an existing classifier map.
            type: str
            required: True
          policer:
            description:
            - A traffic policer to apply to traffic mapping this classifier map.
            type: dict
            suboptions:
              type:
                description:
                - The type of policer. Use "none" to delete the policer.
                type: str
                choices:
                - single_rate
                - twin_rate
                - none
              cir:
                description:
                - The committed information rate in kbps (1-100 000 000). Both types.
                type: int
              cbs:
                description:
                - The committed burst size in bytes (0-16777216). Both types.
                type: int
              ebs:
                description:
                - The excess burst size in bytes (0-16777216). Single-rate only.
                type: int
              pir:
                description:
                - The peak information rate in kbps (1-100000000). Twin-rate only.
                type: int
              pbs:
                description:
                - The peak burst size in bytes (0-16777216). Twin-rate only.
                type: int
              action:
                description:
                - The action to apply to red class traffic.
                type: str
                choices:
                - drop_red
                - remark_transmit
          remark:
            description:
            - An action to remark the CoS in a packet.
            type: dict
            suboptions:
              new_cos:
                description:
                - The new CoS value to use for the packet. Valid values are 0-7.
                type: int
              apply:
                description:
                - Where to apply the CoS, internal - output queue, external - change value in packet, none - delete the remark.
                type: str
                choices:
                - internal
                - external
                - both
                - none
                default: both
          remark_map:
            description:
            - Instructions for remarking packets if policer is active.
            type: list
            elements: dict
            suboptions:
              class:
                description:
                - The traffic class of the packet to be remarked. Any absent class just means no change to those packets.
                type: str
                choices:
                - green
                - yellow
                - red
              new_dscp:
                description:
                - The new DSCP to apply to the packets. Use -1 to indicate no change, valid change values are 0-63.
                type: int
              new_class:
                description:
                - The new traffic class to apply to the packets. Use none to indicate no change.
                type: str
                choices:
                - green
                - yellow
                - red
                - none
          pbr_next_hop:
            description:
            - The IPv4 address to set as the next-hop for matching packets. Use "none" to delete the next hop.
            type: str
          storm_action:
            description:
            - Action to take when triggered by QoS storm protection.
            type: str
            choices:
            - port_disable
            - vlan_disable
            - link_down
            - none
          storm_downtime:
            description:
            - The time in seconds that the storm-action will be applied. Valid 1-86400 (1 day). Use 0 to set default value.
            type: int
            default: 10
          storm_protection:
            description:
            - Whether or not storm protection is enabled. Storm-rate and storm-window must be set before storm protection will operate.
            type: bool
          storm_rate:
            description:
            - The rate, in kbps, at which storm protection will trigger the storm action. Valid values 1-40000000 (1kbps to 40Gbps). Use 0 to reset.
            type: int
          storm_window:
            description:
            - The interval between polls for storm protection, in ms. Valid values are 100-60000 (100ms to 60s). Use 0 to reset.
            type: int
  state:
    description:
    - The state the configuration should be left in
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    default: merged
"""
EXAMPLES = """
# Using Merged

# Before state:
# -------------
#
# awplus#show running-config | begin policy
#
# ...skipping
# policy-map pm1
#  class default
#   remark new-cos 1 both
# !

- name: Prioritise traffic matching classifier am2
  awplus_policy_maps:
    config:
      - name: pm1
        description: "VoIP prioritisation"
        default_action: permit
        classifiers:
          - name: am2
            remark:
              - new_cos: 6
                apply: both
    operation: merged

# After state:
# -------------
#
# awplus#sh running-config | begin policy
#
# ...skipping
# policy-map pm1
#  description "VoIP prioritisation"
#  class default
#   remark new-cos 1 both
#  class am2
#   remark new-cos 6 both
# !


# Using Replaced

# Before state:
# -------------
#
# awplus#sh running-config | begin policy
#
# ...skipping
# policy-map pm1
#  description "VoIP prioritisation"
#  class default
#   remark new-cos 1 both
#  class am2
#   remark new-cos 6 both
# !

- name: Set storm protection on default with replaced
  awplus_policy_maps:
    config:
      - name: pm1
        description: "Storm protection"
        classifiers:
          - name: default
            storm_rate: 10000
            storm_window: 1000
            storm_action: link_down
            storm_protection: true
    operation: replaced

# After state:
# -------------
#
# awplus#sh running-config | begin policy
#
# ...skipping
# policy-map pm1
#  description "Storm protection"
#  class default
#   storm-protection
#   storm-window 1000
#   storm-rate 10000
#   storm-action linkdown
#  class am2
#   remark new-cos 6 both
# !


# Using Overridden

# Before state:
# -------------
#
# awplus#sh running-config | begin policy
#
# ...skipping
# policy-map pm1
#  description "VoIP prioritisation"
#  class default
#   remark new-cos 1 both
#  class am2
#   remark new-cos 6 both
# !

- name: Set storm protection on default with overridden
  awplus_policy_maps:
    config:
      - name: pm1
        description: "Storm protection"
        classifiers:
          - name: default
            storm_rate: 10000
            storm_window: 1000
            storm_action: link_down
            storm_protection: true
    operation: replaced

# After state:
# -------------
#
# awplus#sh running-config | begin policy
#
# ...skipping
# policy-map pm1
#  description "Storm protection"
#  class default
#   storm-protection
#   storm-window 1000
#   storm-rate 10000
#   storm-action linkdown
# !


# Using Deleted

# Before state:
# -------------
#
# awplus#sh running | begin policy
#
# ...skipping
# policy-map storm
#  class default
#   remark new-cos 4 both
# !

- name: Delete a given policy map
  awplus_policy_maps:
    config:
      - name: storm
    operation: deleted

# After state:
# -------------
#
# awplus#show running-config | begin policy
#
# ...skipping
# awplus#


# Using Deleted

# Before state:
# -------------
#
# awplus#sh running | begin policy
#
# ...skipping
# policy-map pm1
#  description "VoIP prioritisation"
#  class default
#   remark new-cos 1 both
#  class am2
#   remark new-cos 6 both
# !

- name: Delete a classifier from a given policy map
  awplus_policy_maps:
    config:
      - name: pm1
        classifiers:
          - name: am2
    operation: deleted

# After state:
# -------------
#
# awplus#show running-config | begin policy
#
# ...skipping
# policy-map pm1
#  description "VoIP prioritisation"
#  class default
#   remark new-cos 1 both
# !


"""
RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The resulting configuration model invocation.
  returned: when changed
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['command 1', 'command 2', 'command 3']
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.policy_maps.policy_maps import Policy_mapsArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.policy_maps.policy_maps import Policy_maps


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=Policy_mapsArgs.argument_spec,
                           supports_check_mode=True)

    result = Policy_maps(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()