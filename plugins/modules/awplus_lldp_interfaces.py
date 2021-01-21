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
The module file for awplus_lldp_interfaces
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
module: awplus_lldp_interfaces
short_description: 'Manages link layer discovery protocol (LLDP) attributes of AlliedWare Plus interfaces'
description: 'This module manages link layer discovery protocol (LLDP) attributes of interfaces on AlliedWare Plus devices.'
version_added: 2.10.4
author: Darryl Alang
notes:
  - 'Tested against AlliedWare Plus AT-x930-28GTX'
options:
  config:
    description: The provided configuration.
    type: list
    elements: dict
    suboptions:
      name:
        description: The full name of the interface.
        type: str
        required: true
      receive:
        description: Enable reception of LLDP advertisements from neighbors.
        type: bool
      transmit:
        description: Enable transmission of LLDP advertisements to neighbors.
        type: bool
      med_tlv_select:
        description: The LLDP-MED TLVs to be transmitted to neighbors.
        type: dict
        suboptions:
          capabilities:
            description: LLDP-MED Capabilities TLV
            type: bool
          inventory_management:
            description: Inventory Management TLV Set
            type: bool
          location:
            description: Location Identification TLV
            type: bool
          network_policy:
            description: Network Policy TLV
            type: bool
          power_management_ext:
            description: Extended Power-Via-MDI TLV
            type: bool
      tlv_select:
        description: The TLVs to be transmitted to neighbors
        type: dict
        suboptions:
          link_aggregation:
            description: Link Aggregation TLV
            type: bool
          mac_phy_config:
            description: MAC/PHY Configuration/Status TLV
            type: bool
          management_address:
            description: Management Address TLV
            type: bool
          max_frame_size:
            description: Maximum Frame Size TLV
            type: bool
          port_and_protocol_vlans:
            description: Port And Protocol VLAN ID TLV
            type: bool
          port_description:
            description: Port Description TLV
            type: bool
          port_vlan:
            description: Port VLAN ID TLV
            type: bool
          power_management:
            description: Power Via MDI TLV
            type: bool
          protocol_ids:
            description: Protocol Identity TLV
            type: bool
          system_capabilities:
            description: System Capabilities TLV
            type: bool
          system_description:
            description: System Description TLV
            type: bool
          system_name:
            description: System Name TLV
            type: bool
          vlan_names:
            description: VLAN Name TLV
            type: bool
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
# TLV Abbreviations:
#   Base:  Pd = Port Description         Sn = System Name
#          Sd = System Description       Sc = System Capabilities
#          Ma = Management Address
#   802.1: Pv = Port VLAN ID             Pp = Port And Protocol VLAN ID
#          Vn = VLAN Name                Pi = Protocol Identity
#   802.3: Mp = MAC/PHY Config/Status    Po = Power Via MDI (PoE)
#          La = Link Aggregation         Mf = Maximum Frame Size
#   MED:   Mc = LLDP-MED Capabilities    Np = Network Policy
#          Lo = Location Identification  Pe = Extended PoE    In = Inventory

# Using merged
#
# Before state:
# -------------
#                                            Optional TLVs Enabled for Tx
#  Port     Rx/Tx  Notif  Management Addr  Base       802.1    802.3    MED       
# --------------------------------------------------------------------------------
#  1.0.1    Rx Tx  -- --  10.38.55.3       ---------- -------- -------- McNpLoPe--
#  1.0.2    -- --  -- --  eccd.6ddf.6d33   --------Ma -------- Mp--La-- McNp--PeIn
#  1.0.3    Rx --  -- --  eccd.6ddf.6d33   ---------- ------Pi -------- Mc--LoPe--
#  1.0.4    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--

- name: Merge provided configuration with device configuration
  alliedtelesis.awplus.awplus_lldp_interfaces:
    config:
      - name: port1.0.2
        receive: true
        med_tlv_select:
          network_policy: false
        tlv_select:
          protocol_ids: true
    state: merged

# After state:
# ------------
#                                            Optional TLVs Enabled for Tx
#  Port     Rx/Tx  Notif  Management Addr  Base       802.1    802.3    MED       
# --------------------------------------------------------------------------------
#  1.0.1    Rx Tx  -- --  10.38.55.3       ---------- -------- -------- McNpLoPe--
#  1.0.2    Rx --  -- --  eccd.6ddf.6d33   --------Ma ------Pi Mp--La-- Mc----PeIn
#  1.0.3    Rx --  -- --  eccd.6ddf.6d33   ---------- ------Pi -------- Mc--LoPe--
#  1.0.4    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--


# Using replaced
#
# Before state:
# -------------
#                                            Optional TLVs Enabled for Tx
#  Port     Rx/Tx  Notif  Management Addr  Base       802.1    802.3    MED       
# --------------------------------------------------------------------------------
#  1.0.1    Rx Tx  -- --  10.38.55.3       ---------- -------- -------- McNpLoPe--
#  1.0.2    -- --  -- --  eccd.6ddf.6d33   --------Ma -------- Mp--La-- McNp--PeIn
#  1.0.3    Rx --  -- --  eccd.6ddf.6d33   ---------- ------Pi -------- Mc--LoPe--
#  1.0.4    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--

- name: Replace provided configuration with device configuration
  alliedtelesis.awplus.awplus_lldp_interfaces:
    config:
      - name: port1.0.3
        transmit: true
    state: replaced

# After state:
# ------------
#                                            Optional TLVs Enabled for Tx
#  Port     Rx/Tx  Notif  Management Addr  Base       802.1    802.3    MED       
# --------------------------------------------------------------------------------
#  1.0.1    Rx Tx  -- --  10.38.55.3       ---------- -------- -------- McNpLoPe--
#  1.0.2    -- --  -- --  eccd.6ddf.6d33   --------Ma -------- Mp--La-- McNp--PeIn
#  1.0.3    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--
#  1.0.4    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--


# Using overridden
#
# Before state:
# -------------
#                                            Optional TLVs Enabled for Tx
#  Port     Rx/Tx  Notif  Management Addr  Base       802.1    802.3    MED       
# --------------------------------------------------------------------------------
#  1.0.1    Rx Tx  -- --  10.38.55.3       ---------- -------- -------- McNpLoPe--
#  1.0.2    -- --  -- --  eccd.6ddf.6d33   --------Ma -------- Mp--La-- McNp--PeIn
#  1.0.3    Rx --  -- --  eccd.6ddf.6d33   ---------- ------Pi -------- Mc--LoPe--
#  1.0.4    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--

- name: Override device configuration of all lldp_interfaces with provided configuration
  alliedtelesis.awplus.awplus_lldp_interfaces:
    config:
      - name: port1.0.1
        receive: false
        transmit: true
        tlv_select:
          protocol_ids: true
    state: overridden

# After state:
# ------------
#                                            Optional TLVs Enabled for Tx
#  Port     Rx/Tx  Notif  Management Addr  Base       802.1    802.3    MED       
# --------------------------------------------------------------------------------
#  1.0.1    -- Tx  -- --  10.38.55.3       ---------- ------Pi -------- McNpLoPe--
#  1.0.2    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--
#  1.0.3    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--
#  1.0.4    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--


# Using Deleted
#
# Before state:
# -------------
#                                            Optional TLVs Enabled for Tx
#  Port     Rx/Tx  Notif  Management Addr  Base       802.1    802.3    MED       
# --------------------------------------------------------------------------------
#  1.0.1    Rx Tx  -- --  10.38.55.3       ---------- -------- -------- McNpLoPe--
#  1.0.2    -- --  -- --  eccd.6ddf.6d33   --------Ma -------- Mp--La-- McNp--PeIn
#  1.0.3    Rx --  -- --  eccd.6ddf.6d33   ---------- ------Pi -------- Mc--LoPe--
#  1.0.4    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--

- name: Delete LLDP attributes of given interfaces
  alliedtelesis.awplus.awplus_lldp_interfaces:
    config:
      - name: port1.0.2
    state: deleted

# After state:
# -------------
#                                            Optional TLVs Enabled for Tx
#  Port     Rx/Tx  Notif  Management Addr  Base       802.1    802.3    MED       
# --------------------------------------------------------------------------------
#  1.0.1    Rx Tx  -- --  10.38.55.3       ---------- -------- -------- McNpLoPe--
#  1.0.2    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--
#  1.0.3    Rx --  -- --  eccd.6ddf.6d33   ---------- ------Pi -------- Mc--LoPe--
#  1.0.4    Rx Tx  -- --  eccd.6ddf.6d33   ---------- -------- -------- McNpLoPe--


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
  sample: ['interface port1.0.2',
           'no lldp transmit',
           'lldp tlv-select port-vlan',
           'no lldp med-tlv-select location']
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.lldp_interfaces.lldp_interfaces import Lldp_interfacesArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.lldp_interfaces.lldp_interfaces import Lldp_interfaces


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=Lldp_interfacesArgs.argument_spec,
                           supports_check_mode=True)

    result = Lldp_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
