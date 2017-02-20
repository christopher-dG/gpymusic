#!/usr/bin/env python3

from getpass import getpass
from gmusicapi import Mobileclient
import warnings

warnings.filterwarnings('ignore')

# Try to print out some valid device IDs.
if __name__ == '__main__':
    api = Mobileclient()
    email = input('Enter your email: ').strip()
    assert '@' in email, 'Invalid email.'
    password = getpass('Enter password for %s: ' % email)

    if not api.login(email, password, Mobileclient.FROM_MAC_ADDRESS):
        print('Login failed, verify your email and password.')
    else:
        devices = api.get_registered_devices()
        for i, device in enumerate(api.get_registered_devices()):
            id = device['id']
            print('%d: %s' % (i + 1, id[2:]if id.startswith('0x') else id))
