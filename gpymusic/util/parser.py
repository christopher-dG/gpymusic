from cmd import Cmd
from enum import Enum


class Command(Enum):
    HELP = 0


class CommandParser(Cmd):
    def do_help(self, line):
        return Command.HELP, line.split()
