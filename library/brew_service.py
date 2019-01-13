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
module: brew_service
author:
    - "Jonathan Nappi (@moogar0880)"
short_description:  Manage macOS services via homebrew service
description:
    - Manages homebrew services on target macOS machines.
options:
    name:
        required: true
        description:
            - Name of the service.
    state:
        required: false
        choices: ['started', 'stopped', 'restarted']
        description:
            - State of the homebrew service
'''

EXAMPLES = '''
- name: ensure dnsmasq is running
  brew_service:
    name: dnsmasq
    state: started
- name: stop dnsmasq service
  brew_service:
    name: dnsmasq
    state: stopped
'''

class ServiceStates(object):
    STARTED = 'started'
    STOPPED = 'stopped'
    RESTARTED = 'restarted'


class BrewService(object):
    def __init__(self, raw_line):
        fields = raw_line.split()
        self.name = fields[0].strip()
        self.status = fields[1].strip()
        self.user = None
        self.plist = None

        # if a user was specified
        if len(fields) >= 3:
            self.user = fields[2].strip()

        # the services plist, if one exists
        if len(fields) >= 4:
            self.plist = fields[3].strip()

    @property
    def running(self):
        return self.status == 'started'


class Homebrew(object):
    """Class responsible for managing interactions with the homebrew"""

    def __init__(self, module):
        self.changed = False
        self.__module = module
        self.__brew = module.get_bin_path('brew', True)
        self.__services = {s.name: s for s in self.list_services()}

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
        """return the desired state of the brew service being managed"""
        return dict(
            started=ServiceStates.STARTED,
            stopped=ServiceStates.STOPPED,
            restarted=ServiceStates.RESTARTED,
            reloaded=ServiceStates.RELOADED,
        ).get(self.params['state'])

    def list_services(self):
        """return the current list of active brew services"""
        cmd = [self.__brew, 'services', 'list']
        rc, out, err = self.run_command(cmd)
        if rc != 0:
            self.fail(changed=self.changed, msg=err.strip())
        return [BrewService(l) for l in out.strip().split('\n')[1:] if l.strip()]

    def start_service(self):
        """ensure the service defined in the module params is running"""
        # do a check upfront to see if the service is already in the desired
        # state. if so, return early, otherwise set the state and update changed
        service = self.__services[self.params['name']]
        if service is not None and service.running:
            return

        cmd = [self.__brew, 'services', 'start', self.params['name']]
        if not self.__module.check_mode:
            rc, out, err = self.run_command(cmd)
            if rc != 0:
                self.fail(changed=self.changed, msg=err.strip())
        self.changed = True

    def stop_service(self):
        """ensure the service defined in the module params is not running"""
        # do a check upfront to see if the service is already in the desired
        # state. if so, return early, otherwise set the state and update changed
        service = self.__services[self.params['name']]
        if service is None or not service.running:
            return

        cmd = [self.__brew, 'services', 'stop', self.params['name']]
        if not self.__module.check_mode:
            rc, out, err = self.run_command(cmd)
            if rc != 0:
                self.fail(changed=self.changed, msg=err.strip())
        self.changed = True

    def restart_service(self):
        """ensure the service defined in the module params is restarted"""
        if not self.__module.check_mode:
            cmd = [self.__brew, 'services', 'restart', self.params['name']]
            rc, out, err = self.run_command(cmd)
            if rc != 0:
                self.fail(changed=self.changed, msg=err.strip())
        self.changed = True

    def manage_service(self):
        # run the method associated with the requested state of the service
        dict(
            started=self.start_service,
            stopped=self.stop_service,
            restarted=self.restart_service,
        )[self.params['state']]()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(
                required=True,
                type='str',
            ),
            state=dict(
                choices=['started', 'stopped', 'restarted'],
                type='str',
            ),
        ),
        supports_check_mode=True,
    )

    brew = Homebrew(module)
    brew.manage_service()

    module.exit_json(
        service=brew.params['name'],
        changed=brew.changed,
    )

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
