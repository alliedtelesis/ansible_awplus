#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
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
The module file for awplus_static_lag_interfaces
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
module: awplus_static_lag_interfaces
version_added: 2.9
short_description: Manage static channel groups on Allied Telesis AlliedWare Plus devices.
description: This module manages properties of static channel groups on Allied Telesis AlliedWare Plus devices.
author: Tony van der Peet
notes:
- Tested against AlliedWare Plus on SBx908NG.
options:
  config:
    description: A list of static channel group configurations.
    type: list
    elements: dict
    suboptions:
      name:
        description:
        - ID of the channel group, in the range 1-248.
        type: str
        required: True
      member-filters:
        description:
        - Allow ACLs and QoS on individual ports, not just the aggregated link.
        type: bool
        required: True
      members:
        description:
        - List of members (switch ports) of the static channel group.
        type: list
        elements: str
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
# awplus#show running-config interface
# interface port1.1.1
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.2
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  static-channel-group 44
# !
# interface sa33,sa44
#  switchport
#  switchport mode access
# !

- name: Merge a new port into a channel group
  awplus_static_lag_interfaces:
    config:
      - name: 33
        members:
          - port1.1.4
        member-filters: false
    operation: merged

# After state:
# -------------
#
# awplus#show running-config interface
# interface port1.1.1
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.2
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  static-channel-group 44
# !
# interface port1.1.4
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface sa33,sa44
#  switchport
#  switchport mode access
# !


# Using Replaced

# Before state:
# -------------
#
# awplus#show running-config interface
# interface port1.1.1
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.2
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  static-channel-group 44
# !
# interface po33,po44
#  switchport
#  switchport mode access
# !

- name: Replace ports in a channel group
  awplus_static_lag_interfaces:
    config:
      - name: 33
        members:
          - port1.1.4
        member-filters: false
    operation: replaced

# After state:
# -------------
#
# awplus#show running-config interface
# interface port1.1.1-1.1.2
#  switchport
#  switchport mode access
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  static-channel-group 44
# !
# interface port1.1.4
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface po33,po44
#  switchport
#  switchport mode access
# !


# Using Overridden

# Before state:
# -------------
#
# awplus#show running-config interface
# interface port1.1.1
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.2
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  static-channel-group 44
# !
# interface sa33,sa44
#  switchport
#  switchport mode access
# !

- name: Override channel group configuration
  awplus_static_lag_interfaces:
    config:
      - name: 33
        members:
          - port1.1.4
        member-filters: false
    operation: overridden

# After state:
# -------------
#
# awplus#show running-config interface
# interface port1.1.1-1.1.3
#  switchport
#  switchport mode access
# !
# interface port1.1.4
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface po33
#  switchport
#  switchport mode access
# !


# Using Deleted

# Before state:
# -------------
#
# awplus#show running-config interface
# interface port1.1.1
#  switchport
#  switchport mode access
#  static-channel-group 33
# !
# interface port1.1.2-1.1.12
#  switchport
#  switchport mode access
# !
# interface port1.2.1-1.2.13
#  switchport
#  switchport mode access
# !
# interface eth0
#  ip address 10.37.153.4/27
# !
# interface po33
#  switchport
#  switchport mode access
# !

- name: Delete a port from a channel group
  awplus_static_lag_interfaces:
    config:
      - name: 33
        members:
        - port1.1.1
        member-filters: false
    operation: deleted

# After state:
# -------------
#
# awplus#show running-config interface
# interface port1.1.1-1.1.12
#  switchport
#  switchport mode access
# !
# interface port1.2.1-1.2.13
#  switchport
#  switchport mode access
# !
# interface eth0
#  ip address 10.37.153.4/27
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
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.static_lag_interfaces.static_lag_interfaces import (
    Static_lag_interfacesArgs
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.static_lag_interfaces.static_lag_interfaces import (
    Static_lag_interfaces
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=Static_lag_interfacesArgs.argument_spec,
                           supports_check_mode=True)

    result = Static_lag_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
