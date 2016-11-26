#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2016, Jonathan Nappi <moogar0880@gmail.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: apm
author:
    - "Jonathan Nappi (@moogar0880)"
short_description: Package manager for APM (Atom Package Manager)
description:
    - Manages APM packages
version_added: "2.0"
options:
    name:
        description:
            - name of package to install/remove/upgrade
        required: false
        default: None
    state:
        description:
            - state of the package
        choices: [ 'present', 'installed', 'latest', 'upgraded', 'absent', 'removed', 'uninstalled' ]
        required: false
        default: 'present'
    upgrade_all:
        description:
            - upgrade all apm packages with available updates
        required: false
        default: 'no'
        choices: [ 'yes', 'no' ]
notes:  []
'''
EXAMPLES = '''
# Install package foo
- apm: name=foo state=present

# Install package foo at a specified version
- apm: name=foo state=present version=1.7.2

# Upgrade all installed packages
- apm: upgrade_all=yes

# Miscellaneous other examples
- apm: name=foo state=absent
- apm: name=foo state=upgraded
'''

class PackageStates(object):
    ABSENT = 'absent'
    INSTALLED = 'installed'
    UPGRADED = 'upgraded'


class APM(object):
    """Class responsible for managing interactions with the a apm install"""

    def __init__(self, module):
        self.__module = module
        self.changed = False

    @property
    def fail(self):
        """alias to the inner ansible module's fail_json method"""
        return self.__module.fail_json

    @property
    def params(self):
        return self.__module.params

    @property
    def run_command(self):
        """alias to the inner ansible module's run_command method"""
        return self.__module.run_command

    @property
    def state(self):
        """return the desired state of the package being managed"""
        state = self.params['state']
        if state in ('present', 'installed'):
            return PackageStates.INSTALLED
        if state in ('latest', 'upgraded'):
            return PackageStates.UPGRADED
        if state in ('absent', 'removed', 'uninstalled'):
            return PackageStates.ABSENT

    def _get_package_name(self, name, version=None):
        """Return an absolute package name for the package and optional version
        provided

        :param name: The name of the package to be installed
        :param version: The optional version for the package to install
        :return: A string of the form {name}@{version}, if a version was
            provied. Otherwise, just the package name is returned
        """
        if version is None:
            return name
        return '{name}@{version}'.format(name=name, version=version)

    @property
    def installed_packages(self):
        """Return a list of the currently installed packages"""
        cmd = ['apm', 'list', '--installed', '--bare']
        rc, out, err = self.run_command(cmd)

        if rc != 0:
            self.fail(changed=self.changed, msg=err.strip())
        return [pkg for pkg in out.split('\n') if pkg.strip()]

    def check_package(self, name, version=None):
        """Determine whether the specified package is currently installed"""
        pkg_name = self._get_package_name(name, version)
        if version is None:
            # check for an absolute package name match
            return pkg_name in self.installed_packages

        # check that the package name is found in the list of installed packages
        return any(pkg_name in p for p in self.installed_packages)

    def install(self, name, version=None):
        pkg_name = self._get_package_name(name, version)
        cmd = ['apm', 'install', pkg_name]
        rc, out, err = self.run_command(cmd)

        if rc != 0:
            self.fail(changed=False, msg=err.strip())
        self.changed = True

    def uninstall(self, name, version=None):
        pkg_name = self._get_package_name(name, version)
        cmd = ['apm', 'uninstall', pkg_name]
        rc, out, err = self.run_command(cmd)

        if rc != 0:
            self.fail(changed=False, msg=err.strip())
        self.changed = True

    def upgrade(self, name=None):
        cmd = ['apm', 'upgrade', '--confirm', 'false']
        if name is not None:
            cmd.append(name)

        rc, out, err = self.run_command(cmd)

        if rc != 0:
            self.fail(changed=False, msg=err.strip())
        self.changed = True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(
                aliases=['pkg', 'package'],
                required=False,
                type='str',
            ),
            version=dict(
                required=False,
                type='str',
                default=None,
            ),
            state=dict(
                default='present',
                choices=['present', 'installed',
                         'latest', 'upgraded',
                         'absent', 'removed', 'uninstalled',
                ],
            ),
            upgrade_all=dict(
                default=False,
                aliases=["upgrade"],
                type='bool',
            )
        ),
        supports_check_mode=True,
    )
    apm = APM(module)
    name, version = apm.params['name'], apm.params['version']

    if module.check_mode:
        changed = apm.check_package(name, version)
        module.exit_json(changed=changed)

    if apm.params['upgrade_all'] or apm.state is PackageStates.UPGRADED:
        apm.upgrade(name)
    elif apm.state is PackageStates.ABSENT:
        installed = apm.check_package(name, version)
        if installed:
            apm.uninstall(name, version)
    elif apm.state is PackageStates.INSTALLED:
        installed = apm.check_package(name, version)
        if not installed:
            apm.install(name, version)

    module.exit_json(changed=apm.changed)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
