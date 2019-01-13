# osx_provision

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

## Roles
The following roles are provided by this repository.

### applications
The applications role installs all homebrew cask apps defined in 
[applications/vars/main.yml](roles/applications/vars/main.yml) and configures 
a custom iterm profile.

### packages
The packages role installs all homebrew packages defined in 
[packages/vars/main.yml](roles/packages/vars/main.yml) and the lastpass cli.

### security
The security role applies various security configuration options to help in
locking down the security of a macOS operating system. Most of the tasks are
based on the recommendations from [macOS Security and Privacy Guide](https://github.com/drduh/macOS-Security-and-Privacy-Guide/blob/master/README.md).

### settings
The settings role configures the default ZSH settings.

### system
The system role configures homebrew, github, system python, system golang and 
sets up a cron job to peridocially run this playbook.
