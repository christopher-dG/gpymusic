from configparser import ConfigParser
from gmusicapi import Mobileclient
from os.path import expanduser, isfile, join
from util import addstr, leave

api = Mobileclient()  # our interface to google music


def login(win):
    user = read_config(win)

    try:
        if not api.login(
                user['email'], user['password'], user['deviceid']
        ):
            addstr(win, 'Login failed: Exiting.')
            leave(2)
    except KeyError:
        addstr(win, 'Config file is missing one or more fields: Exiting.')
        leave(2)

    addstr(win, 'Logged in as %s.' % user['email'])


def read_config(win):  # reads the config file to get login info
    parser = ConfigParser()
    p = join(
        expanduser('~'), '.config', 'pmcli', 'config'
    )
    if not isfile(p):
        addstr(win, 'Config file not found at %s: Exiting.' % p)
        leave(2)

    parser.read(p)
    user_info = {}
    try:
        for key in parser['auth']:
            user_info[key] = parser['auth'][key]
    except KeyError:
        addstr(win, 'Config file is missing [auth] section: Exiting.')
        leave(2)

    return user_info
