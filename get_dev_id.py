from gmusicapi import Mobileclient
import utils, sys

if __name__ == '__main__':
    api = Mobileclient()
    if len(sys.argv) > 1: 
        path = sys.argv[1]
    else:
        path = None
        user_info = utils.API.read_config()
    logged_in = api.login(user_info['email'], user_info['password'], Mobileclient.FROM_MAC_ADDRESS)
    if not logged_in:
        print('login failed')
        print(user_info['email'], user_info['password'], Mobileclient.FROM_MAC_ADDRESS)
        quit()
    devices = api.get_registered_devices()
    count = 1
    for device in devices:
        if device['id'].startswith('0x'):
            print(count, ': ', device['id'][2:])
        else:
            print(count, ': ', device['id'])
        count += 1