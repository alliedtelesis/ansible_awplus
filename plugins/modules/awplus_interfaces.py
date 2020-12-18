#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Allied Telesis Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: alliedtelesis.awplus.awplus_interfaces
author: Cheng Yi Kok (@cyk19)
short_description: Manages attribute of AlliedWare Plus interfaces
description: Manages attribute of AlliedWare Plus network interfaces.
version_added: "2.9"
options:
  config:
    description: A dictionary of interface options.
    type: list
    suboptions:
      name:
        description:
        - Full name of interface, e.g. port1.0.3, vlan2.
        type: str
        required: True
      description:
        description:
        - Interface description.
        type: str
      enabled:
        description:
        - Administrative state of the interface.
        - Set the value to C(true) to administratively enable the interface or C(false) to disable it.
        type: bool
        default: True
      speed:
        description:
        - Interface link speed. Applicable for switchport interfaces only.
        type: str
      mtu:
        description:
        - MTU size for a specific interface. Applicable for VLAN interfaces only.
        - Refer to documentation for valid values.
        type: int
      duplex:
        description:
        - Interface link status. Applicable for switchport interfaces only, either in half duplex,
          full duplex or in automatic state which negotiates the duplex automatically.
        type: str
        choices: ['full', 'half', 'auto']
  state:
    description:
    - The state of the configuration after module completion.
    choices: ['merged', 'replaced', 'overridden', 'deleted']
    default: merged
    type: str
"""

EXAMPLES = """
# Using merged

# Before state:
# ------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.3
#  speed 1000
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.4
#  duplex full
#  switchport
#  switchport mode access
# !
# interface vlan1
#  ip address 192.168.5.2/24
#  ipv6 enable
#  ipv6 address dhcp
#  ip dhcp-client vendor-identifying-class
#  ip dhcp-client request vendor-identifying-specific
# !

- name: Merge provided configuration with device configuration
  alliedtelesis.awplus.awplus_interfaces:
    config:
      - name: port1.0.2
        description: Merged by Ansible Network
        duplex: full

        # vlan1 does not have duplex configuration option
      - name: vlan1
        description: Merged by Ansible Network
        mtu: 234 # in the range <68-1582>
    state: merged

# After state:
# ---------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  description Merged by Ansible Network
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.3
#  speed 1000
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.4
#  duplex full
#  switchport
#  switchport mode access
# !
# interface vlan1
#  description Merged by Ansible Network
#  mtu 234
#  ip address 192.168.5.2/24
#  ipv6 enable
#  ipv6 address dhcp
#  ip dhcp-client vendor-identifying-class
#  ip dhcp-client request vendor-identifying-specific
# !

# Using replaced:

# Before state:
# ---------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  description Merged by Ansible Network
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.3
#  speed 1000
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.4
#  duplex full
#  switchport
#  switchport mode access
# !
# interface vlan1
#  description Merged by Ansible Network
#  ip address 192.168.5.2/24
#  ipv6 enable
#  ipv6 address dhcp
#  ip dhcp-client vendor-identifying-class
#  ip dhcp-client request vendor-identifying-specific
# !

- name: Replace device configuration with provided configuration
  alliedtelesis.awplus.awplus_interfaces:
    config:
      - name: port1.0.3
        description: Replaced by Ansible Network
        duplex: full
        # Available options for speed:
        # 10, 100, 1000, 10000, 100000, (mbps)
        # 2500, 40000, 5000, auto (mbps)
        speed: 1000
        enabled: False

        # vlan1 does not have duplex configuration option
      - name: vlan1
        description: Replaced by Ansible Network
        mtu: 900 # in the range <68-1582>
        enabled: True
    state: replaced

# After state:
# ---------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  description Merged by Ansible Network
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.3
#  description Replaced by Ansible Network
#  speed 1000
#  duplex full
#  shutdown
#  switchport
#  switchport mode access
# !
# interface port1.0.4
#  duplex full
#  switchport
#  switchport mode access
# !
# interface vlan1
#  description Replaced by Ansible Network
#  ip address 192.168.5.2/24
#  ipv6 enable
#  ipv6 address dhcp
#  ip dhcp-client vendor-identifying-class
#  ip dhcp-client request vendor-identifying-specific
# !

# Using overridden

# Before state:
# ------------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  description Merged by Ansible Network
#  duplex full
#  switchport
#  switchport mode trunk
#  switchport trunk allowed vlan add 5-6,13
#  switchport trunk native vlan none
# !
# interface port1.0.3
#  description Replaced by Ansible Network
#  speed 1000
#  duplex full
#  shutdown
#  switchport
#  switchport mode access
# !
# interface port1.0.4-1.0.28
#  switchport
#  switchport mode access
# !
# # interface vlan1
#  ip helper-address 172.26.3.8
# !
# interface vlan2
#  ip address dhcp client-id vlan2 hostname test.com
# !
# interface vlan5
#  description Replaced by Ansible Network
#  mtu 900
# !
# interface vlan13
#  ip address 13.13.13.13/24

- name: Override device configuration of all interfaces with provided configuration
  alliedtelesis.awplus.awplus_interfaces:
    config:
      - name: port1.0.2
        description: Overridden by Ansible Network
        duplex: full
        speed: 2500
        enabled: True

      - name: vlan2
        description: Overridden by Ansible Network
        mtu: 920
        enabled: True
    state: overriden

# After state:
# -------------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  description Overridden by Ansible Network
#  duplex full
#  switchport
#  switchport mode trunk
#  switchport trunk allowed vlan add 5-6,13
#  switchport trunk native vlan none
# !
# interface port1.0.3-1.0.28
#  switchport
#  switchport mode access
# !
# interface vlan1
#  ip helper-address 172.26.3.8
# !
# interface vlan2
#  description Overridden by Ansible Network
#  mtu 920
#  ip address dhcp client-id vlan2 hostname test.com
# !
# interface vlan13
#  ip address 13.13.13.13/24
# !

# Using Deleted

# Before state:
# ---------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  description Merged by Ansible Network
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.3
#  description Replaced by Ansible Network
#  speed 1000
#  duplex full
#  shutdown
#  switchport
#  switchport mode access
# !
# interface port1.0.4
#  description Override by Ansible Network
#  duplex full
#  switchport
#  switchport mode access
# !
# interface vlan1
#  description Override by Ansible Network
#  ip address 192.168.5.2/24
#  ipv6 enable
#  ipv6 address dhcp
#  ip dhcp-client vendor-identifying-class
#  ip dhcp-client request vendor-identifying-specific
# !

- name: Delete module attributes of given interfaces (Note: This won't delete the interface itself)
  alliedtelesis.awplus.awplus_interfaces:
    config:
      - name: port1.0.2
    state: deleted

# After state:
# ---------------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  switchport
#  switchport mode access
# !
# interface port1.0.3
#  description Replaced by Ansible Network
#  speed 1000
#  duplex full
#  shutdown
#  switchport
#  switchport mode access
# !
# interface port1.0.4
#  description Override by Ansible Network
#  duplex full
#  switchport
#  switchport mode access
# !
# interface vlan1
#  description Override by Ansible Network
#  ip address 192.168.5.2/24
#  ipv6 enable
#  ipv6 address dhcp
#  ip dhcp-client vendor-identifying-class
#  ip dhcp-client request vendor-identifying-specific
# !

# Using Deleted without any config passed
# NOTE: This will delete all of configured resource module attributes from each configured interface

# Before state:
# -----------------------
# interface port1.0.1
#  switchport
#  switchport mode access
# !
# interface port1.0.2
#  duplex full
#  switchport
#  switchport mode access
# !
# interface port1.0.3
#  description Replaced by Ansible Network
#  speed 1000
#  duplex full
#  shutdown
#  switchport
#  switchport mode access
# !
# interface port1.0.4
#  description Override by Ansible Network
#  duplex full
#  switchport
#  switchport mode access
# !
# interface vlan1
#  description Override by Ansible Network
#  ip address 192.168.5.2/24
#  ipv6 enable
#  ipv6 address dhcp
#  ip dhcp-client vendor-identifying-class
#  ip dhcp-client request vendor-identifying-specific
# !

- name: "Delete module attributes of given interfaces (Note: This won't delete the interface itself)"
  alliedtelesis.awplus.awplus_interfaces:
    config:
    state: deleted

# After state:
# ---------------------------
# interface port1.0.1-1.0.4
#  switchport
#  switchport mode access
# !
# interface vlan1
#  ip address 192.168.5.2/24
#  ipv6 enable
#  ipv6 address dhcp
#  ip dhcp-client vendor-identifying-class
#  ip dhcp-client request vendor-identifying-specific
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
  sample: ["interface port1.0.10",
          "no duplex"
          "interface port1.0.11",
          "description Merged by Ansible",
          "speed 10"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.config.interfaces.interfaces import (
    Interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=InterfacesArgs.argument_spec, supports_check_mode=True
    )

    result = Interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
