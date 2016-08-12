from gmusicapi import Mobileclient
import configparser, os, sys

def read_config(path=None):
    if not path:
        path = os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'config')
    config = configparser.ConfigParser()
    if not os.path.isfile(path):
        print('Config file not found at ', path, '(exiting).')
        quit()
    config.read(path)
    if not 'User' in config.sections():
        print('Section \'[User]\' not found in ', path, '. See config.example (exiting).')
        quit()
    user_section = config.sections()[0]
    user_options = config.options(user_section)
    user_info = {}
    for option in user_options:
        user_info[option] = config.get(user_section, option)
    return user_info


if __name__ == '__main__':
    api = Mobileclient()
    if len(sys.argv) > 1: 
        path = sys.argv[1]
    else:
        path = None
    user_info = read_config(path)
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
