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
module: launchd
author:
    - "Jonathan Nappi (@moogar0880)"
short_description:  Manage macOS services via launchd
description:
    - Manages launchd services on target macOS machines.
options:
    name:
        required: true
        description:
            - Name of the service.
    state:
        required: false
        choices: [ 'started', 'stopped', 'restarted', 'reloaded' ]
        description:
            - State of the Launchd service
    run_at_load:
        required: false
        choices: [ "yes", "no" ]
        default: null
        description:
            - Whether or not the service should start on boot.
'''

EXAMPLES = '''
- name: ensure dnsmasq is running
  launchd:
    name: com.dnsmasq.dnsmasq
    state: started
- name: disable parental controls
  launchd:
    name: com.apple.familycontrols
    state: stopped
'''

import os
import plistlib

#: The default set of launchd paths. These paths define directories on the
#: target machine where service plists can be found.
LAUNCHD_PATHS = [
    '~/Library/LaunchAgents',
    '/Library/LaunchAgents',
    '/Library/LaunchDaemons',
    '/System/Library/LaunchAgents',
    '/System/Library/LaunchDaemons'
]


class ServiceStates(object):
    STARTED = 'started'
    STOPPED = 'stopped'
    RESTARTED = 'restarted'
    UNLOADED = 'unloaded'


class LaunchdService(object):
    def __init__(self, raw_line):
        fields = raw_line.split()
        self.pid = fields[0]
        self.last_exit_code = fields[1]

        # labels may contain spaces, join any remaining fields as a single label
        self.label = ' '.join(fields[2:])

    @property
    def running(self):
        return self.pid != '-'

    def __repr__(self):
        return '{} {} {}'.format(self.pid, self.last_exit_code, self.label)


class Launchd(object):
    """Class responsible for managing interactions with the launchctl"""

    def __init__(self, module):
        self.changed = False
        self.__module = module
        self.__launchctl = module.get_bin_path('launchctl', True)
        self.__services = {s.label: s for s in self.list_services()}

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
        """return the desired state of the launchd service being managed"""
        return dict(
            started=ServiceStates.STARTED,
            stopped=ServiceStates.STOPPED,
            restarted=ServiceStates.RESTARTED,
            reloaded=ServiceStates.RELOADED,
        ).get(self.params['state'])

    def _get_service_plist(self, service):
        """finds the plist file associated with a service"""
        # get the name of the target file we're searching for
        plist_file_name = '{service}.plist'.format(service=service)

        for path in LAUNCHD_PATHS:
            try:
                files = os.listdir(os.path.expanduser(path))
            except OSError:
                continue

            for filename in files:
                if filename == plist_file_name:
                    return os.path.join(path, filename)

    def list_services(self):
        """return the current list of active launchtl services"""
        cmd = [self.__launchctl, 'list']
        rc, out, err = self.run_command(cmd)
        if rc != 0:
            self.fail(changed=self.changed, msg=err.strip())
        return [LaunchdService(l) for l in out.split('\n')[1:] if l.strip()]

    def run_at_load(self):
        """if specified, set the state of the service's RunAtLoad property"""
        if self.params['run_at_load'] is not None:
            plist_file = self.find_service_plist(self.params['name'])
            if plist_file is None:
                msg = 'unable to find {service} service plist'.format(service=self.params['name'])
                self.__modulemodule.fail_json(msg=msg)

            # ensure the state of the RunAtLoad parameter in the service
            # definition of the plist file
            service_plist = plistlib.readPlist(plist_file)
            enabled = service_plist.get('RunAtLoad', False)

            if self.params['run_at_load'] != enabled:
                if not self.__module.check_mode:
                    service_plist['RunAtLoad'] = self.params['run_at_load']
                    plistlib.writePlist(service_plist, plist_file)
                self.changed = True

    def start_service(self):
        """ensure the service defined in the module params is running"""
        # do a check upfront to see if the service is already in the desired
        # state. if so, return early, otherwise set the state and update changed
        service = self.__services.get(self.params['name'], None)
        if service is not None and service.running:
            return

        cmd = [self.__launchctl, 'start', self.params['name']]
        if not self.__module.check_mode:
            rc, out, err = self.run_command(cmd)
            if rc != 0:
                self.fail(changed=self.changed, msg=err.strip())
        self.changed = True

    def unload_service(self):
        """ensure the service defined in the module params is unloaded"""
        # first ensure the service is stopped
        self.stop_service()
        
        # do a check upfront to see if the service is already in the desired
        # state. if so, return early, otherwise set the state and update changed
        service = self.__services.get(self.params['name'], None)
        if service is None or not service.running:
            return

        plist = self._get_service_plist(self.params['name'])
        if plist is None:
            self.changed = False
            return

        cmd = [self.__launchctl, 'unload', '-f', self.params['name']]
        if not self.__module.check_mode:
            rc, out, err = self.run_command(cmd)
            if rc != 0:
                self.fail(changed=self.changed, msg=err.strip())
        self.changed = True

    def stop_service(self):
        """ensure the service defined in the module params is not running"""
        # do a check upfront to see if the service is already in the desired
        # state. if so, return early, otherwise set the state and update changed
        service = self.__services.get(self.params['name'], None)
        if service is None or not service.running:
            return

        cmd = [self.__launchctl, 'stop', self.params['name']]
        if not self.__module.check_mode:
            rc, out, err = self.run_command(cmd)
            if rc != 0:
                self.fail(changed=self.changed, msg=err.strip())
        self.changed = True

    def restart_service(self):
        """ensure the service defined in the module params is restarted"""
        if not self.__module.check_mode:
            # do a check upfront to see if the service is already in the
            # desired state. if so, return early, otherwise set the state and
            # update changed
            service = self.__services.get(self.params['name'], None)
            cmd = [self.__launchctl, 'kickstart']
            if service is not None and service.running:
                # if the service is already running pass the -k flag to force a
                # restart of the service
                cmd.append('k')
            cmd.append(self.params['name'])
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
            unloaded=self.stop_service,
        )[self.params['state']]()

        # ensure that the service is configured to run at startup as declared
        # by the module parameters. the method call handled dealing with an
        # unspecified run_at_load parameter
        self.run_at_load()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(
                required=True,
                type='str',
            ),
            state=dict(
                choices=['started', 'stopped', 'restarted', 'unloaded'],
                type='str',
            ),
            run_at_load=dict(
                required=False,
                type='bool',
            )
        ),
        supports_check_mode=True,
    )

    launchd = Launchd(module)
    launchd.manage_service()

    module.exit_json(
        service=launchd.params['name'],
        changed=launchd.changed,
    )

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
