#!/usr/bin/env python2

import sys
import os
import getopt
import getpass
import urllib
import urllib2
import cookielib
from bs4 import BeautifulSoup


# Most pfSense systems are deployed using a self-signed certificate
# Patch SSL verification to trust self-signed certs if necessary
#
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

class PFSenseBackup(object):
    """
    Authenticates with a pfSense installation and exports the configuration.
    """

    def __init__(self, server, timeout, username, password):
        """
        Authenticates with the pfSense server.
        """
        self.server = server
        self.timeout = timeout
        cj = cookielib.CookieJar()
        cookies = urllib2.HTTPCookieProcessor(cj)
        self.site = urllib2.build_opener(cookies)
        self._authenticate(username, password)
    
    def backup_config(self, directory = None, target_file = None, rrd = None):
        backup_page = self.server + '/diag_backup.php'
        backup_file = self._get_backup_file(directory, target_file)
        csrf_token = self._get_csrf_token(backup_page)
        backup_options = self._get_backup_options(rrd, csrf_token)
        with open(backup_file, 'w') as output:
            try:
                resp = self.site.open(backup_page, backup_options, self.timeout)
                output.writelines(resp)
            except Exception as e:
                print "Error backing up configuration: {0}".format(e)
                sys.exit(1)
                

    def _get_backup_file(self, directory, target_file):
        backup_file = target_file
        if backup_file == None:
            backup_file = 'pfsense-backup.xml'
        if directory != None:
            backup_file = os.path.join(directory, backup_file)
        return backup_file

    def _get_backup_options(self, rrd, csrf_token):
        options = {}
        options['__csrf_magic'] = csrf_token
        options['backuparea'] = '' # Backup everything
        if rrd:				
            options['donotbackuprrd'] = '' # Clear the option to skip rrd data if we want to include it
        else:
            options['donotbackuprrd'] = 'on' # otherwise, make sure it's enabled
        options['Submit'] = 'Download configuration'
        return urllib.urlencode(options)

    def _get_csrf_token(self, page):
        try:
            result = self.site.open(page, timeout = self.timeout)
        except Exception as e:
            print "Error loading page: {0}".format(e)
            sys.exit(1)
        html = result.read()
        parsed = BeautifulSoup(html, 'html.parser')
        csrf_input = parsed.body.find('input', attrs={'name':'__csrf_magic'})
        csrf_token = None
        try:
            csrf_token = csrf_input.attrs['value']
        except IndexError:
            pass
        return csrf_token

    def _authenticate(self, username, password):
        login_page = self.server + '/index.php'
        csrf_token = self._get_csrf_token(login_page)
        input_params = {}
        input_params['login'] = 'Login'
        input_params['__csrf_magic'] = csrf_token
        input_params['usernamefld'] = username
        input_params['passwordfld'] = password
        login_data = urllib.urlencode(input_params)
        try:
            result = self.site.open(login_page, login_data, self.timeout)
        except Exception as e:
            print "Error logging in: {0}".format(e)
            sys.exit(1)
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
            Example: https://pfsense.example.com
        
        -t <seconds> | --timeout <seconds>
            Timeout for network requests.

        -u <username> | --username <username>
        
        -p <password> | --password <password>

        -d | --directory <directory>
            Defaults to current directory.

        -r | --rrd
            Include RRD Data
        
	-f | --file <file>
            Defaults to 'pfsense-backup.xml'.

    """

def _options(args):
    """Processes command line arguments"""

    try:
        opts, args = getopt.gnu_getopt(args, 's:t:u:p:d:f:rh',
          ['server=', 'timeout=', 'username=', 'password=', 'directory=', 'file=', 'rrd', 'help'])
    except getopt.GetoptError, e:
        print str(e)
        _usage()
        sys.exit(2)

    # Defaults
    server = timeout = username = password = directory = target_file = rrd = None
    
    for o,v in opts:
        if o in ('-s', '--server'):
            server = v
        elif o in ('-t', '--timeout'):
            try:
                timeout = int(v)
            except: 
                print "Timeout specified is not an integer."
                sys.exit(2)
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
        elif o in ('-r', '--rrd'):
            rrd = True
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

    # remove trailing slash from server path if present
    server = server.rstrip('/')

    return (server, timeout, username, password, directory, target_file, rrd)

if __name__ == '__main__':
    server, timeout, username, password, directory, target_file, rrd = _options(sys.argv[1:])
    exporter = PFSenseBackup(server, timeout, username, password)
    exporter.backup_config(directory, target_file, rrd)
