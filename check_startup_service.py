#!/usr/bin/env python3

# check_startup_service ; -*-Python-*-
# a simple nagios check to verify if init scripts are running
# python 3 enhanced version of check_init_service
# Copyright James Powell 2023 / jamespo [at] gmail [dot] com
# This program is distributed under the terms of the GNU General Public License v3

import sys
import re
import os
from optparse import OptionParser

class CheckInitService(object):
    def __init__(self, options):
        self.services = options.services.split(',')
        self.expected_services = set()
        self.rogue_services = set()
        self.matchregex = options.matchregex
        self.svccmd = options.svccmd

    @staticmethod
    def _findservice():
        '''return full path to service command'''
        for svc in ('/bin/systemctl', '/usr/sbin/service', '/sbin/service'):
            if os.path.isfile(svc):
                return svc
        return None

    @staticmethod
    def build_cmdline(svc_cmd, servicename, username = None):
        """create cmdline to check service, if username is set
        create user check"""
        if svc_cmd == "/bin/systemctl":
            if username:
                # user systemd checks require sudo
                svc_cmd = 'sudo %s --user -M %s@' % (svc_cmd, username)
            return "%s is-active %s" % (svc_cmd, servicename)
        else:
            return '/usr/bin/sudo -n ' + svc_cmd + ' ' + servicename + ' status 2>&1'

    @staticmethod
    def parse_servicename(servicename):
        """check if service is user or has negation, returns
        running_is_expected, clean_servicename, username"""
        running_is_expected = True
        if '/' in servicename:
            username, clean_servicename = servicename.split('/')
        else:
            username = None
            clean_servicename = servicename
        # check for negation (ie - service NOT running, ^ prefix)
        if clean_servicename[0] == '^':
            clean_servicename = clean_servicename[1:]
            running_is_expected = False
        return clean_servicename, running_is_expected, username

    def checkinits(self):
        '''check init scripts statuses'''
        if self.svccmd is None: 
            svc_cmd = self._findservice()
        else:
            svc_cmd = self.svccmd
        # loop round all the services
        for servicename in self.services:
            clean_servicename, running_is_expected, username = self.parse_servicename(servicename)
            cmdline = self.build_cmdline(svc_cmd, clean_servicename, username)
            # print(cmdline) # DEBUG
            initresults = [line.strip() for line in os.popen(cmdline).readlines()]
            # check for "running" regex in output
            for res in initresults:
                if re.search(self.matchregex, res) is not None:
                    if running_is_expected:
                        self.expected_services.add(servicename)
                    else:
                        self.rogue_services.add(servicename)
                    break
            # if running regex not found, check if negation applies
            if servicename not in self.expected_services and servicename \
               not in self.rogue_services:
                if running_is_expected:
                    self.rogue_services.add(servicename)
                else:
                    # not running and that's OK
                    self.expected_services.add(servicename)
        # if # of ok results == # of services checked, all ok
        if len(self.expected_services) == len(self.services):
            return 0
        else:
            return 1

def main():
    parser = OptionParser()
    parser.add_option("--services", dest="services", help="service1,service2")
    parser.add_option("--matchregex", dest="matchregex", default="(?:^active|is running|start/running)",
        help="regex to match running service status")
    parser.add_option("--svccmd", dest="svccmd", help="full path to command to run for check")
    options, _ = parser.parse_args()
    if options.services is None:
        print("UNKNOWN: No services specified")
        sys.exit(2)
    ci = CheckInitService(options)
    rc = ci.checkinits()
    if rc == 0:
        rcstr = 'OK: all services as expected (' + ','.join(ci.expected_services) + ')'
    else:
        rcstr = 'CRITICAL: Rogue (' +  ','.join(ci.rogue_services) + ')'
        if len(ci.expected_services) > 0:
            rcstr += ' Expected (' + ','.join(ci.expected_services) + ')'
    print(rcstr)
    sys.exit(rc)

if __name__ == '__main__':
    main()

