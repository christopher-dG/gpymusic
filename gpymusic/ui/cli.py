import gpymusic.util as util

HELP = """\
Commands
========
* help [cmd]: Show this help message, or one for cmd\
"""
HELP_CMDS = {
    "help": HELP,
}


class CLI:
    def __init__(self, config):
        # config is an instance of gpymusic.util.Config.
        self.parser = util.CommandParser()
        self.commands = {
            util.Command.HELP: self._help,
        }
        self.options = self._parse_config(config.ui_settings)

    def command_loop(self):
        """
        The main input loop.
        Take in strings and route them to the appropriate method.
        """
        while True:
            # It would make sense to use self.parser.cmdloop,
            # but the parser doesn't know which methods need to be run.
            try:
                instruction = input("> ")
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                break
            if not instruction:
                continue
            if instruction.split()[0] in HELP_CMDS:
                cmd, args = self.parser.onecmd(instruction)
                self.commands[cmd](*args)
            else:
                print("Unknown command")

    def _help(self, *args):
        """
        Show the general help message, or the help message for the first
        argument if applicable.
        """
        if not args:
            print(HELP)
        else:
            if args[0] in HELP_CMDS:
                print(HELP_CMDS[args[0]])
            else:
                print(HELP)

    def _parse_config(self, settings):
        """Parse the settings from a dict."""
        options = {}
        if "colour" in settings:
            options["colour"] = settings["colour"]
        elif "color" in settings:
            options["colour"] = settings["color"]
        else:
            self.colour = False
        return options
