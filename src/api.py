from configparser import ConfigParser
from gmusicapi import Mobileclient
from os.path import expanduser, isfile, join
from util import addstr, leave

api = Mobileclient()  # Our interface to Google Music.


def login(win):
    """
    Log in to Google Play Music.

    Arguments:
    win: Window on which to display output.
    """
    user = read_config(win)  # Login information.

    try:
        if not api.login(
                user['email'], user['password'], user['deviceid']
        ):  # Login failed;
            addstr(win, 'Login failed: Exiting.')
            leave(2)
    except KeyError:  # Invalid config file.
        addstr(win, 'Config file is missing one or more fields: Exiting.')
        leave(2)

    addstr(win, 'Logged in as %s.' % user['email'])  # Login succeeded.


def read_config(win):
    """
    Parses a config file for login information.
      Config file should be located at '~/.config/pmcli/config'
      with a section called [auth] containing email, password, and deviceid.

    Arguments:
    win: Window on which to display output.

    Returns: A dict containing keys 'email', 'password', and 'deviceid'.
    """
    parser = ConfigParser()
    config = join(expanduser('~'), '.config', 'pmcli', 'config')

    if not isfile(config):
        addstr(win, 'Config file not found at %s: Exiting.' % config)
        leave(2)

    parser.read(config)
    user_info = {}

    try:
        for key in parser['auth']:  # Read login information.
            user_info[key] = parser['auth'][key]
    except KeyError:  # Invalid config file.
        addstr(win, 'Config file is missing [auth] section: Exiting.')
        leave(2)

    return user_info
