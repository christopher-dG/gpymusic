from gmusicapi import Mobileclient
# Imports are stupid.
mc = Mobileclient()  # noqa Our interface to Google Play Music.

from . import songqueue
from . import view
from . import writer

from os.path import expanduser, join


# Location where we keep songs, playlists, libraries, and source code.
DATA_DIR = join(expanduser('~'), '.local', 'share', 'gpymusic')
# Location where we keep user and mpv configurations.
CONFIG_DIR = join(expanduser('~'), '.config', 'gpymusic')

q = songqueue.Queue()  # Queue/playlist.
w = writer.Writer(None, None, None, None, curses=False)  # Output handler.
v = view.View()  # Main window contents.
client = None  # To be set be main.py.
