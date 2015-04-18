Overview
========

Authenticates with a [pfSense](http://www.pfsense.org/) server and exports
a backup of the configuration and statistics. If the required options aren't
specified, they will be promped for interactively.

Configure cron to run this script with the necessary parameters to backup your
pfSense configuration and stastics on a regular basis.

**NOTE**: RRD data is no longer included by default, but can be included via command line option. See below for more details.

Requirements
============

Requires BeautifulSoup to be installed:

    pip install BeautifulSoup

Compatability
=============

This has been updated to support the new CSRF token in the pfSense login page and tested with 2.1.3-RELEASE, 2.1.5-RELEASE, and 2.2.2-RELEASE.

Usage
=====

    Usage: pfsense-backup.py OPTIONS

    OPTIONS:

        -h | --help

        -s <server url> | --server <server url>
            The base URL for the pfSense installation.
            Example: https://pfsense.example.com/

        -u <username> | --username <username>
        
        -p <password> | --password <password>

        -d | --directory <directory>
            Defaults to current directory.

        -r | --rrd
            Includes RRD data with the backup.

        -f | --file <file>
            Defaults to 'pfsense-backup.xml'

