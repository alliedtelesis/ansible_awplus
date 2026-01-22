=============================================================
Allied Telesis Alliedware Plus (AW+) Collection Release Notes
=============================================================

.. contents:: Topics

v1.3.0
======

Major Changes
-------------

- Updated project to use Python >= 3.12.
- Updated project to use Ansible-core >= 2.19.4.
- Added idempotency integration tests and fixes for multiple modules.
- Strictened the behaviour of each state for multiple modules.

Minor Changes
-------------

- Fixed info messages causing an error when running commands through Ansible.
- awplus_openflow - Idempotency fixes.
- awplus_user - Idempotency fixes, defaults to SHA512 hashing, small fixes.
- awplus awplus_static_lag_interfaces - Idempotency and behavioural changes.
- awplus_lacp_interfaces - Idempotency and behavioural changes.
- awplus_lacp - Idempotency and behavioural changes, added optional global-passive-mode parameter.


Deprecated Modules
------------------

- awplus_rip - Deprecated and to be deleted in the following version.

Deleted Modules
---------------

New Modules
-----------

- awplus_policy_maps - Resource module for configuring policy maps.
- awplus_premark_dscps - Resource module for configuring premark DSCP maps.
- awplus_policy_interfaces - Resource module for configuring QoS policies for interfaces.
- awplus_l2_interfaces - Resource module for the L2 configuation of interfaces.
- awplus_static_route - Resource module for configuring static routes.
- awplus_mlag - Resource module for configuring MLAG.
- awplus_vxlan - Resource module for configuring VXLAN.

v1.2.2
======

Minor Changes
-------------

- improved tests in awplus_user module
- improved tests in awplus_openflow module
- minor improvements to Github workflow
- replace all formatting strings with f-strings

Bugfixes
--------

- awplus_l2_interfaces - Check for stackports before applying configuation.
- awplus_user - Support password hashing correctly.

Deleted Modules
---------------

New Modules
-----------

- awplus_acl - Resource module for ACLs.
- awplus_acl_interfaces - Resource module for configuring ACLs to interfaces.
- awplus_class_maps - Resource module for classifier maps.

v1.2.1
======

Minor Changes
-------------

- awplus_facts - Add interface speed to legacy facts
- awplus_l2_interfaces - Support native VLAN none on trunk mode
- awplus_l2_interfaces - Add playbook tests and a playbook test runner

Bugfixes
--------

- awplus_l2_interfaces - Support list of allowed VLANs correctly

Deleted Modules
---------------

New Modules
-----------

v1.2.0
======

Minor Changes
-------------

- awplus_facts - Reinstate legacy facts
- awplus_openflow - Reimplement as resource module

Bugfixes
--------

- Fixed exceptions when no existing configuration exists for a module
- Fixed exception when device doesn't support BGP
- Fixed parsing serial number and model when model has embedded spaces

Deleted Modules
---------------

New Modules
-----------

v1.1.0
======

Minor Changes
-------------

- awplus_banner - Reimplement as resource module
- awplus_bgp - Reimplement as resource module
- awplus_commands - Improvements
- awplus_config - Improvements
- awplus_facts - Support only resource modules
- awplus_interfaces - Reimplement as resource module
- awplus_l2_interfaces - Reimplement as resource module
- awplus_l3_interfaces - Reimplement as resource module
- awplus_lacp - Reimplement as resource module
- awplus_lacp_interfaces - Reimplement as resource module
- awplus_lag_interfaces - Reimplement as resource module
- awplus_lldp_global - Reimplement as resource module
- awplus_lldp_interfaces - Reimplement as resource module
- awplus_logging - Reimplement as resource module
- awplus_ntp - Reimplement as resource module
- awplus_openflow - Improvements
- awplus_static_lag_interfaces - Reimplement as resource module
- awplus_user - Reimplement as resource module
- awplus_vlans - Reimplement as resource module

Bugfixes
--------

Deleted Modules
---------------

- awplus_linkagg - Manage link aggregation groups on AW+ devices (duplicates awplus_lag_interfaces so can be removed)
- awplus_vrf - Manage VRFs on AW+ devices (replaced by awplus_vrfs)

New Modules
-----------

- awplus_vrfs - Resource module for VRFs on AW+ devices

v1.0.0
======

New Plugins
-----------

Cliconf
~~~~~~~

- awplus - Use awplus cliconf to run command on AW+ platform

New Modules
-----------

- awplus_banner - Manage multiline banners on AW+ devices
- awplus_bgp - Manage BGP on AW+ devices
- awplus_command - Run arbitrary commands on an AW+ device
- awplus_config - Manage AW+ configuration sections
- awplus_facts - Collect facts from remote devices running AW+
- awplus_interfaces - Manage interfaces on AW+ devices
- awplus_ipv6_ospf - Manage OSPFv3 on AW+ devices
- awplus_l2_interfaces - Manage L2 interfaces on AW+ devices
- awplus_l3_interfaces - Manage L3 interfaces on AW+ devices
- awplus_lacp - Manage LACP on AW+ devices
- awplus_lacp_interfaces - Manage LACP interfaces on AW+ devices
- awplus_lag_interfaces - Manage LAG interfaces on AW+ devices
- awplus_linkagg - Manage link aggregation groups on AW+ devices
- awplus_lldp_global - Manage LLDP global parameters on AW+ devices
- awplus_lldp_interfaces - Manage LLDP interfaces on AW+ devices
- awplus_logging - Manage logging on AW+ devices
- awplus_ntp - Manage Network Time Protocol on AW+ devices
- awplus_openflow - Manage OpenFlow on AW+ devices
- awplus_ospf - Manage OSPFv2 on AW+ devices
- awplus_ping - Manage PING on AW+ devices
- awplus_rip - Manage RIP on AW+ devices
- awplus_static_lag_interfaces - Manage static LAG interfaces on AW+ devices
- awplus_static_route - Manage static IP routes on AW+ devices
- awplus_system - Manage the system attributes on AW+ devices
- awplus_user - Manage local users on AW+ devices
- awplus_vlans - Manage VLANs on AW+ devices
- awplus_vrf - Manage VRFs on AW+ devices
