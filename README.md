osx_provision
=============

Ansible playbook for provisioning a local OS X system.

Note: You will be asked to enter your sudo password in order to run this playbook.

To run the playbook manually, run:

```bash
$ ansible-playbook --ask-sudo-pass -i inventory local.yml --connection=local
```

If bootstrapping a node for the first time, run the bootstrap.sh script:

```bash
$ bootstrap.sh
```
And be prepared to wait a while.
