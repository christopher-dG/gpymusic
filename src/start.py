import curses as crs
import consts
from getpass import getpass
from os.path import basename, isfile, join
from time import sleep
import json
import sys


def validate_config(config):
    """
    Verify that a config file has all necessary data.
      If the check fails, the program ends.

    Arguments:
    config: Config to be checked.

    Returns: Whether or not the config file has colour support.
    """

    def validate_colour(hex):
        """
        Verify that a string represents a valid hex colour.

        Arguments:
        hex: String to be checked.

        Returns: Whether or not the string is a hex colour.
        """
        # ASCII values for letters and numbers.
        c = tuple(range(48, 58)) + tuple(range(65, 91)) + tuple(range(97, 123))

        return (hex.startswith('#') and len(hex) == 7 and
                all([ord(ch) in c for ch in hex[1:]]))

    user_fields = ['email', 'password', 'deviceid']
    colour_fields = ['background', 'foreground',
                     'highlight', 'content1', 'content2']

    # Check if there is any user info.
    if 'user' not in config:
        consts.w.goodbye('No user info in config file: Exiting.')

    # Check if there is enough user info.
    if not all([k in config['user'] for k in user_fields]):
        consts.w.goodbye('Missing user info in config file: Exiting.')

    # Check if there is any colour info.
    if 'colour' in config and 'enable' not in config['colour']:
        consts.w.goodbye('Missing colour enable flag in config file: Exiting.')
    else:
        colour = config['colour']['enable'] == 'yes'

    # Check if the colours are valid.
    if colour and not all([c in config['colour'] for c in colour_fields]):
        consts.w.outbar_msg(
            'One or more colours are missing: Not using colour.')
        colour = False
        sleep(1.5)
    elif colour and not all([validate_colour(config['colour'][c])
                             for c in colour_fields]):
        consts.w.outbar_msg(
            'One or more colours are invalid: Not using colour.')
        colour = False
        sleep(1.5)

    return colour


def password(config):
    """
    Prompt the user for their password if it is not supplied
      in their config file.

    Arguments:
    config: Dict of config info.

    Returns: the config dict, either unchanged or with
      the entered password.
    """
    if not config['user']['password']:
        if not consts.w.curses:
            try:
                config['user']['password'] = getpass()
            except KeyboardInterrupt:
                consts.w.goodbye('Exiting.')
        else:
            crs.noecho()  # Don't show the password as it's entered.
            consts.w.addstr(consts.w.inbar, 'Enter your password: ')
            try:
                config['user'][
                    'password'] = consts.w.inbar.getstr().decode('utf-8')
            except KeyboardInterrupt:
                consts.w.gooodbye('Exiting.')
            crs.echo()

    return config


def read_config():
    """
    Parses a config file for login information.
      Config file should be located at '~/.config/pmcli/config'
      with a section called[auth] containing email, password,
      and deviceid.

    Returns: A dict containing keys 'user' and 'colour''.
    """
    path = join(consts.CONFIG_DIR, 'config.json')
    if not isfile(path):
        consts.w.goodbye('Config file not found at %s: Exiting.' %
                         basename(path))

    with open(path) as f:
        try:
            config = json.load(f)
        except json.decoder.JSONDecodeError:
            consts.w.goodbye('Invalid config file, please refer to '
                             'config.example: Exiting.')

    return password(config)


def get_windows():
    """
    Initialize the curses windows.

    Returns: Curses windows.
    """
    main = crs.initscr()  # Forthe bulk of output.
    main.resize(crs.LINES - 3, crs.COLS)
    inbar = crs.newwin(1, crs.COLS, crs.LINES - 1, 0)  # For user input.
    infobar = crs.newwin(1, crs.COLS, crs.LINES - 2, 0)  # For 'now playing'.
    outbar = crs.newwin(1, crs.COLS, crs.LINES - 3, 0)  # For notices.
    return main, inbar, infobar, outbar


def hex_to_rgb(hex):
    """
    Convert a hex colour to(r, g, b).

    Arguments:
    hex: Hexidecimal colour code, i.e. '#abc123'.

    Returns: (r, g, b) tuple with values 0 - 1000.
    """

    scalar = 3.9215  # 255 * 3.9215 ~= 1000.
    r = int(int(hex[1:3], 16) * scalar)
    g = int(int(hex[3:5], 16) * scalar)
    b = int(int(hex[5:7], 16) * scalar)

    return (r, g, b)


def set_colours(colours):
    """
    Set curses colours.

    Arguments:
    colours: Dict with colour information.
    """
    global w
    crs.start_color()
    # Define colours.
    crs.init_color(0, *hex_to_rgb(colours['background']))
    crs.init_color(1, *hex_to_rgb(colours['foreground']))
    crs.init_color(2, *hex_to_rgb(colours['highlight']))
    crs.init_color(3, *hex_to_rgb(colours['content1']))
    crs.init_color(4, *hex_to_rgb(colours['content2']))

    # Define colour pairs.
    crs.init_pair(1, 1, 0)
    crs.init_pair(2, 2, 0)
    crs.init_pair(3, 3, 0)
    crs.init_pair(4, 4, 0)

    # Set colours.
    crs.start_color()
    consts.w.main.bkgdset(' ', crs.color_pair(1))
    consts.w.inbar.bkgdset(' ', crs.color_pair(1))
    consts.w.infobar.bkgdset(' ', crs.color_pair(2))
    consts.w.outbar.bkgdset(' ', crs.color_pair(4))

    consts.w.refresh()


def easy_login():
    """One - step login for debugging."""
    config = (password(read_config()))
    validate_config(config)
    user = config['user']

    if not consts.mc.login(user['email'], user['password'], user['deviceid']):
        print('Login failed: exiting.')
        sys.exit()
    else:
        print('Logged in as %s (%s).' %
              (user['email'], 'Full' if consts.mc.is_subscribed else 'Free'))


def login(user):
    """
    Log into Google Play Music. Succeeds or exits.

    Arguments:
    user: Dict containing auth information.
    """
    crs.curs_set(0)
    consts.w.outbar_msg('Logging in...')
    if not consts.mc.login(user['email'], user['password'], user['deviceid']):
        consts.w.goodbye('Login failed: Exiting.')
    consts.w.outbar_msg('Logging in... Logged in as %s (%s).' % (
        user['email'], 'Full' if consts.mc.is_subscribed else 'Free'))
