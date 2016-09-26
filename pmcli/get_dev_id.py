from gmusicapi import Mobileclient
import api_user


if __name__ == '__main__':  # print out some valid device IDs
    user_info = api_user.APIUser.read_config()
    if not api_user.API.login(user_info['email'], user_info['password'], Mobileclient.FROM_MAC_ADDRESS):
        print('login failed, check your config file')
        quit()
    devices = api_user.API.get_registered_devices()
    i = 1
    for device in devices:
        if device['id'].startswith('0x'):
            print('%d: %s' % (i, device['id'][2:]))
        else:
            print('%d: %s' % (i, device['id']))
        i += 1
