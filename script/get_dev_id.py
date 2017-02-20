#!/usr/bin/env python3

from gmusicapi import Mobileclient
from getpass import getpass
import warnings
warnings.simplefilter('ignore')

# Try to print out some valid device IDs.
if __name__ == '__main__':
    api = Mobileclient()
    email = input('Enter your email: ')
    password = getpass('Enter your password: ')

    if not api.login(email, password, Mobileclient.FROM_MAC_ADDRESS):
        print('Login failed, verify your email and password:'
              'enter any key to exit.')
        quit()

    devices = api.get_registered_devices()
    for i in range(len(devices)):
        print('%d: %s' % (
            i, devices[i]['id'][2:]
            if devices[i]['id'].startswith('0x') else devices[i]['id'])
        )
