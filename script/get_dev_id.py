#!/usr/bin/env python3

from getpass import getpass
from gmusicapi import Mobileclient
from warnings import filterwarnings

filterwarnings('ignore')

# Try to print out some valid device IDs.
if __name__ == '__main__':
    mc = Mobileclient()
    email = input('Enter your email: ').strip()
    assert '@' in email, 'Invalid email.'
    password = getpass('Enter password for %s: ' % email)

    if not mc.login(email, password, mc.FROM_MAC_ADDRESS):
        print('Login failed, verify your email and password.')
        quit()

    for i, id in enumerate([
            d['id'][2:] if d['id'].startswith('0x') else d['id'].replace(':', '')  # noqa
            for d in mc.get_registered_devices()
    ]):
        print('%d: %s' % (i + 1, id))
