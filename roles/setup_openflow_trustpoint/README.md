awplus.setup_openflow_trustpoint
=========

This role sets up a trustpoint for OpenFlow, which is required for SSL connections. Future work would involve this automating the process of generating a trustpoint and signing the certificate, but this currently does not seem possible. 

Requirements
------------

Currently this requires that a trustpoint is already setup and there is a peer certificate on the device which has been signed by the same CA as the OpenFlow controller.

Role Variables
--------------

```
  trustpoint_name: The name of the already configured trustpoint
  controller_peer_certificate: The path to the peer certificate signed by the controller's CA
```

Example Playbook
----------------

    - hosts: all
      roles:
        - setup_openflow_trustpoint

License
-------

GPLv3
