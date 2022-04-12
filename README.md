# Allied Telesis AlliedWare Plus (AW+) Collection

The Ansible Allied Telesis AW+ collection includes a variety of Ansible content to help automate the management of Allied Telesis network devices.

## Version compatibility

This collection has been tested against AW+ 5.5.2.

This collection has been tested against Ansible version: **>=2.9.10**.

<!--
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
-->

### Supported connections

The Allied Telesis AlliedWare Plus collection supports ``network_cli`` connections.

## Included content

### Cliconf plugins
Name | Description
--- | ---
alliedtelesis.awplus.cliconf|Use awplus cliconf to run command on AW+ platform

### Filter plugins
Name | Description
--- | ---

### Httpapi plugins
Name | Description
--- | ---

### Modules
Name | Description
--- | ---
alliedtelesis.awplus.awplus_banner|Manage multiline banners on Allied Telesis AW+ devices
alliedtelesis.awplus.awplus_bgp|Configure global BGP protocol settings on Allied Telesis AW+
alliedtelesis.awplus.awplus_command|Run arbitrary commands on an Allied Telesis AW+ device
alliedtelesis.awplus.awplus_config|Manage Allied Telesis AW+ configuration sections
alliedtelesis.awplus.awplus_facts|Collect facts from remote devices running Allied Telesis AW+
alliedtelesis.awplus.awplus_interfaces|Interfaces resource module
alliedtelesis.awplus.awplus_ipv6_ospf|OSPFv3 resource module
alliedtelesis.awplus.awplus_l2_interfaces|L2 interfaces resource module
alliedtelesis.awplus.awplus_l3_interfaces|L3 interfaces resource module
alliedtelesis.awplus.awplus_lacp|LACP resource module
alliedtelesis.awplus.awplus_lacp_interfaces|LACP interfaces resource module
alliedtelesis.awplus.awplus_lag_interfaces|LAG interfaces resource module
alliedtelesis.awplus.awplus_lldp_global|LLDP resource module
alliedtelesis.awplus.awplus_lldp_interfaces|LLDP interfaces resource module
alliedtelesis.awplus.awplus_logging|Manage logging on Allied Telesis AW+ devices
alliedtelesis.awplus.awplus_ntp|Network Time Protocol resource module
alliedtelesis.awplus.awplus_openflow|Manage OpenFlow on network devices
alliedtelesis.awplus.awplus_ospf|OSPFv2 resource module
alliedtelesis.awplus.awplus_ping|Use ping utility from this Allied Telesis AW+ device
alliedtelesis.awplus.awplus_rip|RIP resource module
alliedtelesis.awplus.awplus_static_lag_interfaces|Static LAG interfaces resource module
alliedtelesis.awplus.awplus_static_routes|Static routes resource module
alliedtelesis.awplus.awplus_system|Manage the system attributes on Allied Telesis AW+ devices
alliedtelesis.awplus.awplus_user|Manage the collection of local users on Allied Telesis AW+ devices
alliedtelesis.awplus.awplus_vlans|VLANs resource module
alliedtelesis.awplus.awplus_vrfs|VRF resource module

### Inventory plugins
Name | Description
--- | ---


## Installing this collection

You can install the Allied Telesis AlliedWare Plus collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install alliedtelesis.awplus

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: alliedtelesis.awplus
```

## Using this collection

This collection includes [network resource modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html).

### Using modules from the Allied Telesis AlliedWare Plus collection in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN), such as `alliedtelesis.awplus.awplus_l2_interfaces`.

The following task replaces configuration changes in the running configuration on an Allied Telesis AW+ network device, using the FQCN:

```yaml
---
  - name: Replace device configuration of specified L2 interfaces with provided configuration.
    alliedtelesis.awplus.awplus_l2_interfaces:
      config:
        - name: port1.0.1
          trunk:
            allowed_vlans: 20-25,40
            native_vlan: 20
      state: replaced
```

**NOTE**: For Ansible 2.9, you may not see deprecation warnings when you run your playbooks with this collection.

<!-- Use this documentation to track when a module is deprecated. -->

### See Also:

* [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [Allied Telesis AlliedWare Plus collection repository](https://github.com/alliedtelesis/ansible_awplus). See [Contributing to Ansible-maintained collections](https://docs.ansible.com/ansible/devel/community/contributing_maintained_collections.html#contributing-maintained-collections) for complete details.

See the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html) for details on contributing to Ansible.

### Code of Conduct
This collection follows the Ansible project's
[Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).
Please read and familiarize yourself with this document.

## Release notes

Release notes are available [here](https://github.com/alliedtelesis/ansible_awplus/blob/master/CHANGELOG.rst).

## Roadmap

<!--
 Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle.
-->

## More information

- [Ansible network resources](https://docs.ansible.com/ansible/latest/network/getting_started/network_resources.html)
- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
