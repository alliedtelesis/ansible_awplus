# Allied Telesis AWPlus Collection

![Build and Test](https://github.com/alliedtelesis/ansible_awplus/workflows/Build%20and%20Test/badge.svg)

- [Usage](#usage)
- [Development](#development)
- [Running playbooks](#running-playbooks)
- [Running unit tests](#running-unit-tests)
  - [Running a specific unit test](#running-a-specific-unit-test)
  - [Running all unit tests](#running-all-unit-tests)

## Usage

TODO

## Development

Create the `ansible_collections` directory structure and clone:

```bash
user@machine:~/Repos$ mkdir -p ansible_collections/alliedtelesis
user@machine:~/Repos$ cd ansible_collections/alliedtelesis
user@machine:~/Repos/ansible_collections/alliedtelesis$ git clone git@github.com:alliedtelesis/ansible_awplus.git awplus
```

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
user@machine:~/Repos/ansible_collections/alliedtelesis$ python -m pip install virtualenv
user@machine:~/Repos/ansible_collections/alliedtelesis$ python3 -m pip install virtualenv
user@machine:~/Repos/ansible_collections/alliedtelesis$ mkdir venvs

user@machine:~/Repos/ansible_collections/alliedtelesis$ python -m virtualenv venvs/virtualenv-2.7 --python=python
user@machine:~/Repos/ansible_collections/alliedtelesis$ source venvs/virtualenv-2.7/bin/activate
user@machine:~/Repos/ansible_collections/alliedtelesis$ python -m pip install -r requirements.txt
user@machine:~/Repos/ansible_collections/alliedtelesis$ python -m pip install -r ~/Repos/ansible/requirements.txt
user@machine:~/Repos/ansible_collections/alliedtelesis$ python -m pip install -r ~/Repos/ansible/test/units/requirements.txt

user@machine:~/Repos/ansible_collections/alliedtelesis$ python3 -m virtualenv venvs/virtualenv-3.6 --python=python3.6
user@machine:~/Repos/ansible_collections/alliedtelesis$ source venvs/virtualenv-3.6/bin/activate
user@machine:~/Repos/ansible_collections/alliedtelesis$ python3 -m pip install -r requirements.txt
user@machine:~/Repos/ansible_collections/alliedtelesis$ python3 -m pip install -r ~/Repos/ansible/requirements.txt
user@machine:~/Repos/ansible_collections/alliedtelesis$ python3 -m pip install -r ~/Repos/ansible/test/units/requirements.txt
```

## Running playbooks

```bash
user@machine:~/Repos/ansible_collections/alliedtelesis$ ansible-playbook playbooks/awplus_ipv6_ospf.yml -vvv
```

## Running unit tests

- Make sure that `source hacking/env-setup` has been run.
- Make sure that you only run a specific version of Python, and have activated the relevant virtualenv.

### Running a specific unit test

```bash
user@machine:~/Repos/ansible_collections/alliedtelesis$ source venvs/virtualenv-3.6/bin/activate
user@machine:~/Repos/ansible_collections/alliedtelesis$ ansible-test units tests/unit/modules/test_awplus_linkagg.py --python 3.6
```

### Running all unit tests

```bash
user@machine:~/Repos/ansible_collections/alliedtelesis$ source venvs/virtualenv-2.7/bin/activate
user@machine:~/Repos/ansible_collections/alliedtelesis$ ansible-test units --python 2.7
```
