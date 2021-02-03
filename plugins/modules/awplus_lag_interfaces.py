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
The module file for awplus_lag_interfaces
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
module: awplus_lag_interfaces
version_added: 2.9
short_description: Manage dynamic channel groups on Allied Telesis AlliedWare Plus devices.
description: This module manages properties of dynamic channel groups on Allied Telesis AlliedWare Plus devices.
author: Tony van der Peet
notes:
- Tested against AlliedWare Plus on SBx908NG.
options:
  config:
    description: A list of dynamic channel group configurations.
    type: list
    elements: dict
    suboptions:
      name:
        description:
        - ID of the channel group, in the range 1-248.
        type: str
        required: True
      members:
        description:
        - List of members (switch ports) of the dynamic channel group.
        type: list
        elements: dict
        suboptions:
          member:
            description:
            - Interface name of member of the dynamic channel group.
            type: str
            required: True
          mode:
            description:
            - LACP mode for the channel group.
            type: str
            required: True
            choices:
            - active
            - passive
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
#  channel-group 33 mode active
# !
# interface port1.1.2
#  switchport
#  switchport mode access
#  channel-group 33 mode passive
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  channel-group 44 mode active
# !
# interface po33,po44
#  switchport
#  switchport mode access
# !

- name: Merge a new port into a channel group
  alliedtelesis.awplus.awplus_lag_interfaces:
    config:
      - name: 33
        members:
          - member: port1.1.4
            mode: active
    state: merged

# After state:
# -------------
#
# awplus#show running-config interface
# interface port1.1.1
#  switchport
#  switchport mode access
#  channel-group 33 mode active
# !
# interface port1.1.2
#  switchport
#  switchport mode access
#  channel-group 33 mode passive
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  channel-group 44 mode active
# !
# interface port1.1.4
#  switchport
#  switchport mode access
#  channel-group 33 mode active
# !
# interface po33,po44
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
#  channel-group 33 mode active
# !
# interface port1.1.2
#  switchport
#  switchport mode access
#  channel-group 33 mode passive
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  channel-group 44 mode active
# !
# interface po33,po44
#  switchport
#  switchport mode access
# !

- name: Replace ports in a channel group
  alliedtelesis.awplus.awplus_lag_interfaces:
    config:
      - name: 33
        members:
          - member: port1.1.4
            mode: active
    state: replaced

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
#  channel-group 44 mode active
# !
# interface port1.1.4
#  switchport
#  switchport mode access
#  channel-group 33 mode active
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
#  channel-group 33 mode active
# !
# interface port1.1.2
#  switchport
#  switchport mode access
#  channel-group 33 mode passive
# !
# interface port1.1.3
#  switchport
#  switchport mode access
#  channel-group 44 mode active
# !
# interface po33,po44
#  switchport
#  switchport mode access
# !

- name: Override channel group configuration
  alliedtelesis.awplus.awplus_lag_interfaces:
    config:
      - name: 33
        members:
          - member: port1.1.4
            mode: active
    state: overridden

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
#  channel-group 33 mode active
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
#  channel-group 33 mode active
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

- name: Delete a given channel group
  alliedtelesis.awplus.awplus_lag_interfaces:
    config:
      - name: 33
    state: deleted

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
  sample: ['interface port1.0.2', 'channel-group 3 mode passive']

"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.lag_interfaces.lag_interfaces import Lag_interfacesArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.lag_interfaces.lag_interfaces import Lag_interfaces


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=Lag_interfacesArgs.argument_spec,
                           supports_check_mode=True)

    result = Lag_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
