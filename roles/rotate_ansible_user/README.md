awplus.rotate_ansible_user
=========

This role is used to rotate the user account that Ansible uses for SSH connections by creating a new
user and deleting the old user.

Requirements
------------

Role Variables
--------------

```
  new_username: Username of the new user
  new_password: Password of the new user
```

Example Playbook
----------------

    - hosts: all
      roles:
        - rotate_ansible_user

License
-------

GPLv3
