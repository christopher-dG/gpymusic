import sys


def err(s):
    """Print `s` as an error and exit."""
    print(s, file=sys.stderr)
    sys.exit(1)


from .config import Config  # noqa
from .parser import Command  # noqa
from .parser import CommandParser  # noqa
