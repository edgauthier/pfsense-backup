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
        Authenticates with the pfSense server.
        """
        self.server = server
        self._authenticate(username, password)
    
    def backup_config(self, directory = None, target_file = None):
        backup_page = self.server + '/diag_backup.php'
        backup_file = self._get_backup_file(directory, target_file)
        backup_options = self._get_backup_options()
        with open(backup_file, 'w') as output:
            resp = self.site.open(backup_page, backup_options)
            output.writelines(resp)

    def _get_backup_file(self, directory, target_file):
        backup_file = target_file
        if backup_file == None:
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

    def _authenticate(self, username, password):
        cj = cookielib.CookieJar()
        self.site = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        login_data = urllib.urlencode({'usernamefld' : username, 'passwordfld' : password, 'login' : 'Login'})
        login_page = self.server + '/index.php'
        result = self.site.open(login_page, login_data)
        if "username or password incorrect" in result.read().lower():
            print "Invalid username or password"
            sys.exit(1)

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

        -f | --file <file>
            Defaults to 'pfsense-backup.xml'.

    """

def _options(args):
    """Processes command line arguments"""

    try:
        opts, args = getopt.getopt(args, 's:u:p:d:f:h',['server=','username=','password=','directory=','file=','help'])
    except getopt.GetoptError, e:
        print str(e)
        _usage()
        sys.exit(2)

    # Defaults
    server = username = password = directory = target_file = None
    
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
        elif o in ('-f', '--file'):
            target_file = v
        elif o in ('-h', '--help'):
            _usage()
            sys.exit(2)
        else:
            _usage()
            sys.exit(2)

    # prompt for missing parameters
    if not server:
        server = raw_input('Server URL: ')
    if not username:
        username = raw_input('Username: ')
    if not password:
        password = getpass.getpass('Password: ')

    return (server, username, password, directory, target_file)

if __name__ == '__main__':
    server, username, password, directory, target_file = _options(sys.argv[1:])
    exporter = PFSenseBackup(server,username,password)
    exporter.backup_config(directory, target_file)
