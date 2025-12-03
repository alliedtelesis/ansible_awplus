awplus.configure_openflow_with_hybrid_port_and_amf
=========

This role configures OpenFlow with hybrid ports and AMF - following example #2 from [OpenFlow Allied Telesis Documentation](https://www.alliedtelesis.com/us/en/documents/openflow-feature-overview-and-configuration-guide).

Requirements
------------

Role Variables
--------------

```
  controller_name: Name of the controller
  controller_ip: IP of the controller
  controller_l4_port: L4 port of the controller
  native_vlan_id: Native VLAN id 
  legacy_ports_vlan_id: Legacy ports VLAN id
  openflow_ports: List of ports for OpenFlow
  amf_link_port: Port for AMF
  inactivity_timer: Inactivity timer for OpenFlow
  fail_mode: Fail mode for OpenFlow # secure, standalone, or secure_nre
  openflow_protocol: Protocol used by OpenFlow # tcp or ssl
```

Example Playbook
----------------

    - hosts: all
      roles:
        - configure_openflow_with_hybrid_port_and_amf

License
-------

GPLv3
