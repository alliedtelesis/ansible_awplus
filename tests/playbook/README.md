Tests that use the test playbooks. General idea is that each test playbook has an entry that
gets the system into a particular state, then a number of entries that make changes to that
initial state. Tests consist of getting the system into the initial state, then running a
single playbook and checking the commands generated.

The test playbook and the wrapper code that repeatedly runs playbooks reside in this
directory. In order to run these, an appropriate ansible.cfg and hosts file should be
placed in this directory. Note that the test playbook will reference a particular host
name, so this has to be seen in the hosts file.
