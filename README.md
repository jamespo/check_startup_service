check_startup_service
=====================

Usage
-----

Checks on a Linux system whether services in init are running.

	USAGE: check_startup_service --services service1,service2


	PARAMETERS:

		--services
			comma separated list of services to check, at least one required

		--matchregex
			optional regular expression to match against service svcname status
			output. Defaults to (?:is running|start/running)

		--svccmd
			optional. specify the "service" command for your OS (eg on Centos 7
			this would be /bin/systemctl, on Centos 6 /sbin/service, otherwise
			it will try & guess)

You can also check if services are NOT running (eg for DR) by prefixing them with ^


Install
-------

If you are not using systemctl (Systemd) but classic init you must have a sudo entry for the user running this check (eg nagios). Also ensure that you disable requiring a tty for this user in sudoers

	Defaults:nagios !requiretty
	nagios ALL = NOPASSWD: /sbin/service * status
