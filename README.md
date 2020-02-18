# Allied Telesis AWPlus Collection

![Build and Test](https://github.com/alliedtelesis/ansible_awplus/workflows/Build%20and%20Test/badge.svg)

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
  - [Running unit tests](#running-unit-tests)
    - [Running a specific unit test](#running-a-specific-unit-test)
    - [Running all unit tests](#running-all-unit-tests)
  - [Running playbooks](#running-playbooks)
  - [Connecting to AlliedWare Plus devices](#connecting-to-alliedware-plus-devices)
    - [SSH](#ssh)
  - [Basic Ansible Usage](#basic-ansible-usage)
  - [Developing modules](#developing-modules)
  - [Building and installing locally](#building-and-installing-locally)
  - [Linting and Formatting](#linting-and-formatting)
    - [PEP 8 checks](#pep-8-checks)
    - [yamllint](#yamllint)
    - [ansible-lint](#ansible-lint)
    - [Formatting](#formatting)

This is an [Ansible Collection](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) of various library modules which can interact with AlliedWare Plus devices.

## Installation

Distribution is via [Ansible Galaxy](https://galaxy.ansible.com/). To install this collection, please use the following command:

```bash
ansible-galaxy collection install alliedtelesis.awplus
```

## Usage

To use this collection, make sure to update your host inventory with `ansible_network_os=awplus`.

Documentation for each module can be found within [`plugins/modules`](https://github.com/alliedtelesis/ansible_awplus/tree/master/plugins/modules). Playbooks used for testing can be found in [`playbooks`](https://github.com/alliedtelesis/ansible_awplus/tree/master/playbooks).

Commands interact with the AW+ CLI, and are thus closely related.

## Contributing

Create the `ansible_collections` directory structure and clone:

```bash
user@machine:~/Repos$ mkdir -p ansible_collections/alliedtelesis
user@machine:~/Repos$ cd ansible_collections/alliedtelesis
user@machine:~/Repos/ansible_collections/alliedtelesis$ git clone git@github.com:alliedtelesis/ansible_awplus.git awplus
```

> Cloning into the above directory structure means that tools like `ansible-test` work.

Clone Ansible, and checkout the latest stable branch:

```bash
user@machine:~/Repos$ git clone git@github.com:ansible/ansible.git
user@machine:~/Repos/ansible$ cd ansible
user@machine:~/Repos/ansible$ git checkout stable-2.9
```

Setup the Ansible hacking tools:

```bash
user@machine:~/Repos/ansible$ source hacking/env-setup
```

Create the Python virtual environments for the versions of Python you're intending to use:

```bash
python -m pip install virtualenv
python3 -m pip install virtualenv
mkdir venvs

python -m virtualenv venvs/virtualenv-2.7 --python=python
source venvs/virtualenv-2.7/bin/activate
python -m pip install -r ~/Repos/ansible/requirements.txt
python -m pip install -r ~/Repos/ansible/test/units/requirements.txt
python -m pip install -r ~/Repos/ansible/test/lib/ansible_test/_data/requirements/units.
python -m pip install -r ~/Repos/ansible/test/lib/ansible_test/_data/requirements/

python3 -m virtualenv venvs/virtualenv-3.6 --python=python3.6
source venvs/virtualenv-3.6/bin/activate
python3 -m pip install -r ~/Repos/ansible/requirements.txt
python3 -m pip install -r ~/Repos/ansible/test/units/requirements.txt
python3 -m pip install -r ~/Repos/ansible/test/lib/ansible_test/_data/requirements/units.txt
python3 -m pip install -r ~/Repos/ansible/test/lib/ansible_test/_data/requirements/network-integration.txt
```

### Running unit tests

- Make sure that `source hacking/env-setup` has been run.
- Make sure that you only run a specific version of Python, and have activated the relevant virtualenv.

#### Running a specific unit test

```bash
source venvs/virtualenv-3.6/bin/activate
ansible-test units tests/unit/modules/test_awplus_linkagg.py --python 3.6
```

Moved it out into its own folder within docs/

#### Running all unit tests

```bash
source venvs/virtualenv-2.7/bin/activate
ansible-test units --python 2.7
```

### Running playbooks

```bash
ansible-playbook playbooks/awplus_ipv6_ospf.yml -vvv
```

### Connecting to AlliedWare Plus devices

Boot up your AW+ device. If you're an Allied Telesis developer and you don't have a device set up, search for `Find an AW+ device` in the internal wiki - it should be in a page called `Training - Linux PC`.

Once the AW+ device is booted, ensure that the device is connected using port 1.

Now, its IP address can be configured:

```
awplus>enable
awplus#configure terminal
awplus(config)#interface vlan1
awplus(config-if)#ip address A.B.C.D/netmask
```

`A.B.C.D` should appropriately based on the ethernet interface on the engineer's machine to which the AW+ device is attached to.

For example:

```bash
user@machine:~$ ifconfig
...
eno1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.1  netmask 255.255.255.0  broadcast 192.168.1.255
        ether 38:2c:4a:70:2a:ea  txqueuelen 1000  (Ethernet)
        RX packets 40221  bytes 2701459 (2.7 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 41066  bytes 59018157 (59.0 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 20  memory 0xdfd00000-dfd20000
...
```

Thus, an appropriate IP address for the AW+ device is `192.168.1.2/24`. If the interface does not have an IPv4 address, add one.

After the IP address of the AW+ is configured, the following should work from the engineer's PC:

```bash
user@machine:~$ ping 192.168.1.2  # The IP address of the AW+ device.
PING 192.168.1.2 (192.168.1.2) 56(84) bytes of data.
64 bytes from 192.168.1.2: icmp_seq=1 ttl=64 time=0.421 ms
64 bytes from 192.168.1.2: icmp_seq=2 ttl=64 time=0.252 ms
...
```

Additionally, the pinging from the AW+ device should work:

```
awplus>ping 192.168.1.1  # The IP address of the engineer's PC.
```

#### SSH

Now that the interfaces are connected, using SSH from the engineer's PC should work:

```bash
user@machine:~$ ssh manager@192.168.1.2
```

Additionally, using SSH from the AW+ device should work:

```
awplus>ssh username@192.168.1.1
```

### Basic Ansible Usage

In order to actually use Ansible, create a basic inventory:

```bash
mkdir /etc/ansible/
sudo vim /etc/ansible/hosts # Or your preferred editor.
```

Add the following lines to `/etc/ansible/hosts`:

```ini
[all:vars]
ansible_connection=network_cli

[switches:children]
awplus

[awplus]
aw1 ansible_host=192.168.1.2 # The IP address of configured AWPlus device.

[awplus:vars]
ansible_become=yes
ansible_become_method=enable
ansible_network_os=awplus
ansible_user=USERNAME # NOTE: Do this yourself
ansible_password=PASSWORD # NOTE: Do this yourself
```

To test this configuration, go to the terminal where Ansible can be run from source, eitherwise:

```bash
user@machine:~$ cd Repos/ansible  # Where you cloned Ansible to.
user@machine:~/Repos/ansible$ source hacking/env-setup
```

Once in the appropriate terminal:

```bash
user@machine:~/ansible$ ansible all -m ping
```

This should give the following output:

```bash
aw1 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}
```

Now, create `ansible.cfg`:

```bash
sudo vim /etc/ansible/ansible.cfg
```

Populate `ansible.cfg` with:

```ini
[defaults]
inventory       = /etc/ansible/hosts
forks           = 5
poll_interval   = 1
ask_pass        = False
transport       = smart
remote_user     = manager
become          = yes
become_user     = root
interpreter_python = auto_legacy_silent
host_key_checking = False


collections_path   = ~/.ansible/collections/ansible_collections
terminal_plugins   = ~/.ansible/collections/ansible_collections/alliedtelesis/awplus/plugins/terminal
cliconf_plugins    = ~/.ansible/collections/ansible_collections/alliedtelesis/awplus/plugins/cliconf
```

### Developing modules

Ideally, read the [Developer Guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html) in the Ansible documentation.

Definitely read the [getting started](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#environment-setup) page.

Additionally, read the [Developing collections](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html#developing-collections) page.

It's also a good idea to take a look at the existing modules (NOTE: `awplus_ospf` and `awplus_ipv6_ospf` differ in implementation from the others quite drastically).

### Building and installing locally

Remove any existing collections of the same version:

```bash
rm -r ~/.ansible/collections/ansible_collections/alliedtelesis/awplus
```

Remove the virtualenvs (make sure to install them again for unit testing):

```bash
rm -r venvs
```

Build the collection:

```bash
ansible-galaxy collection build
```

Install the collection:

```bash
ansible-galaxy collection install alliedtelesis-awplus-VERSION.tar.gz
# For example, ansible-galaxy collection install alliedtelesis-awplus-1.0.0.tar.gz
```

### Linting and Formatting

To use linting and formatting, please install the contents of [`dev-requirements.txt`](./dev-requirements.txt):

The content score of this collection is affected by the yamllint and ansible-lint results.

```bash
python -m pip install -r dev-requirements.txt # In which virtualenv you're using.
```

#### PEP 8 checks

```bash
ansible-test sanity --test pep8 plugins/ tests/
```

For more, see https://docs.ansible.com/ansible/latest/dev_guide/testing_pep8.html.

#### yamllint

```bash
yamllint -c yamllint.yaml .
```

#### ansible-lint

```bash
ansible-lint playbooks
```

#### Formatting

Formatting is done using [Black](https://black.readthedocs.io/en/stable/). Either use if from the Python extension for Visual Studio Code, or from the commandline:

```bash
black .
```
