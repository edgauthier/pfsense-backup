#!/usr/bin/python

import sys
import os
import getopt
import getpass
import urllib
import urllib2
import cookielib

class PFSenseBackup(object):
    """
    Authenticates with a pfSense installation and exports the configuration.
    """

    def __init__(self, server, username, password):
        """
        Stores the username and password, and then authenticates.
        """
        self.server = server
        self.username = username
        self.password = password
        self._authenticate()
    
    #TODO - export config
    def backup_config(self, directory = None):
        backup_page = self.server + '/diag_backup.php'
        backup_file = self._get_backup_file(directory)
        backup_options = self._get_backup_options()
        with open(backup_file, 'w') as output:
            resp = self.site.open(backup_page, backup_options)
            output.writelines(resp)

    def _get_backup_file(self, directory):
        backup_file = 'pfsense-backup.xml'
        if directory != None:
            backup_file = os.path.join(directory, backup_file)
        return backup_file

    def _get_backup_options(self):
        options = {}
        options['backuparea'] = ''
        options['donotbackuprrd'] = ''
        options['Submit'] = 'Download configuration'
        return urllib.urlencode(options)

    def _authenticate(self):
        cj = cookielib.CookieJar()
        self.site = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        login_data = urllib.urlencode({'usernamefld' : self.username, 'passwordfld' : self.password, 'login' : 'Login'})
        login_page = self.server + '/index.php'
        self.site.open(login_page, login_data)
        #TODO test if the login succeeded

def _usage():
    print """
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

    """

def _options(args):
    """Processes command line arguments"""

    try:
        opts, args = getopt.getopt(args, 's:u:p:d:h',['server=','username=','password=','directory=','help'])
    except getopt.GetoptError, e:
        print str(e)
        _usage()
        sys.exit(2)

    # Defaults
    server = username = password = directory = None
    
    for o,v in opts:
        if o in ('-s', '--server'):
            server = v
        elif o in ('-u', '--username'):
            username = v
        elif o in ('-p', '--password'):
            password = v
        elif o in ('-d', '--directory'):
            if os.path.exists(v):
                directory = v
            else:
                print "Destination directory does not exist."
                sys.exit(2)
        elif o in ('-h', '--help'):
            _usage()
            sys.exit(2)
        else:
            _usage()
            sys.exit(2)

    # prompt for missing parameters if missing
    if not server:
        server = raw_input('Server URL: ')
    if not username:
        username = raw_input('Username: ')
    if not password:
        password = getpass.getpass('Password: ')

    return (server, username, password, directory)

if __name__ == '__main__':
    server, username, password, directory = _options(sys.argv[1:])
    exporter = PFSenseBackup(server,username,password)
    exporter.backup_config(directory)
