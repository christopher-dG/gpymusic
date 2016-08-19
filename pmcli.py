import sys
from backend import  MusicObject
from backend import API


class CommandStack:

    def __init__(self):
        self.stack = []

    def push(self, command):
        self.stack.append(command)

    def pop(self):
        if len(stack) == 1:
            self.stack = []
        else:
            self.stack = self.stack[:-1]

    def peek(self):
        if len(self.stack) < 1:
            return None
        return self.stack[-1]
        
    def is_empty(self):
        return len(self.stack) == 0

    def flush(self):
        self.stack = []

class FrontEnd:

    def __init__(self, path=None):
        self.api = API(path)
        self.commands = CommandStack()
        self.something_useful = ''
        
    def print_help(self):
        print('usage:')
        print('/ : search')
        print('q: quit')

    def input_loop(self):
        self.commands.push(input('> '))
        process_command():
        if not process_command():
            print('Invalid command')
            self.commands.pop()

    def process_command(self):
        command = self.commands.peek()
        if not isinstance(self.something_useful, MusicObject) or not isinstance(self.something_useful, dict):
            return False
        else:
            pass # do stuff
        if command.startswith('/'):
            self.something_useful = self.api.search(command[1:])
        return True

    def is_num(self, command):
        try:
            int(command)
            return True
        except ValueError as e:
            return False
    
    def search(self, query):
        return self.api.search(query)

    def get_num(self, valid_range):
        valid = False
        while not valid:
            num = input('> ')
            try:
                num = int(num)
                if num > 0 and num <= valid_range:
                    valid = True
                else:
                    print('Out of range. Enter a number 1-', valid_range)
            except ValueError as e:
                print ('Invalid input. Enter a number 1-', valid_range)
        return num
        
if __name__ == '__main__':
    print('Welcome to (P)lay (M)usic for (CLI)!')
    if len(sys.argv) > 1:
        pm = FrontEnd(sys.argv[1])
    else:
        pm = FrontEnd()

    while True:
        print('calling input loop')
        pm.input_loop()
