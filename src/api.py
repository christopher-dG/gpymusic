from configparser import ConfigParser
from gmusicapi import Mobileclient
from os.path import expanduser, isfile, join

api = Mobileclient()  # our interface to google music


def login():
    user = read_config()

    try:
        if not api.login(
                user['email'], user['password'], user['deviceid']
        ):
            input('Login failed: enter any key to exit.')
            quit()
    except KeyError:
        print('Config file is missing email, password, or device ID: '
              'enter any key to exit.')
        quit()

    return user['email']


def read_config():  # reads the config file to get login info
    parser = ConfigParser()
    path = join(
        expanduser('~'), '.config', 'pmcli', 'config'
    )
    if not isfile(path):
        input('Config file not found at %s: press any key to exit.'
              % path)
        quit()

    parser.read(path)
    user_info = {}
    try:
        for key in parser['auth']:
            user_info[key] = parser['auth'][key]
    except KeyError:
        input('Config file is missing [auth] section: press any key to exit.')
        quit()

    return user_info
