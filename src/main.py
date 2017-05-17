#! /usr/bin/env python3

import client
import common
import start


if __name__ == '__main__':
    start.check_dirs()
    common.w.replace_windows(*start.get_windows())
    common.w.curses = True
    config = start.read_config()
    colour = start.validate_config(config)
    if colour:
        start.set_colours(config['colour'])
        common.w.colour = True
    common.w.welcome()
    start.login(config['user'])
    common.w.addstr(
        common.w.infobar,
        'Enter \'h\' or \'help\' if you need help.'
    )

    common.client = client.FullClient() if (
        common.mc.is_subscribed
    ) else client.FreeClient()

    while True:
        common.client.transition()

else:
    start.easy_login()
