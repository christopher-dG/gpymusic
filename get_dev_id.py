import getpass
from gmusicapi import Mobileclient


# Try to print out some valid device IDs.
if __name__ == '__main__':
    api = Mobileclient()
    email = input('Enter your email: ').strip()
    assert '@' in email, 'Please enter a valid email.'
    password = getpass.getpass('Enter password for {}: '.format(email))

    if not api.login(email, password, Mobileclient.FROM_MAC_ADDRESS):
        print('Login failed, verify your email and password: '
              'enter any key to exit.')
        quit()

    for i, device in enumerate(api.get_registered_devices()):
        d_id = device['id']
        print('%d: %s' % (i + 1, d_id[2:] if d_id.startswith('0x') else d_id))
