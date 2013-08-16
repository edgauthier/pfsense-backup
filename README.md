Overview
========

Authenticates with a [pfSense](http://www.pfsense.org/) server and exports
a backup of the configuration and statistics. If the required options aren't
specified, they will be promped for interactively.

Configure cron to run this script with the necessary parameters to backup your
pfSense configuration and stastics on a regular basis.

Compatability
=============

This has only been tested against pfSense 2.0.1.

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

        -f | --file <file>
            Defaults to 'pfsense-backup.xml'

