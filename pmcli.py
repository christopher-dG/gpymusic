import sys
from backend import API

def print_help():
    print('usage:')
    print('/ : search')
    print('q: quit')

def input_loop(last_command):
    if not last_command:
        last_command = input('> ')
    elif last_command.startswith('/'):
        results = api.search(last_command[1:])
        valid_range = 0
        for key in results:
            valid_range += len(results[key])
        try:
            last_command = int(input('> '))
        except ValueError as e:
            print('Enter a number 1-', valid_range)
        
    return last_command
        
if __name__ == '__main__':
    print('Welcome to (P)lay (M)usic for (CLI)!')
    if len(sys.argv) > 1:
        api = API(sys.argv[1])
    else:
        api = API()
    last_command = None
    while True:
        last_command = input_loop(last_command)
