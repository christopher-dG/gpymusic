from gmusicapi import Mobileclient
import api_user


if __name__ == '__main__':  # print out some valid device IDs
    user_info = api_user.APIUser.read_config()

    try:
        if not api_user.API.login(user_info['email'], user_info['password'],
                                  Mobileclient.FROM_MAC_ADDRESS):
            input('Login failed, check your config file email and password:'
                  'enter any key to exit.')
            quit()
    except KeyError:
        print('Config file is missing email, password, or device ID: '
              'enter any key to exit.')
        quit()

    devices = api_user.API.get_registered_devices()
    i = 1

    for device in devices:
        print('%d: %s' % (
            i, device['id'][2:] if device['id'].startswith('0x')
            else device['id']))
        i += 1
