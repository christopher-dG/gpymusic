from gmusicapi import Mobileclient

import songqueue
import view
import writer

from os.path import expanduser, join


# Location where we keep songs, playlists, libraries, and source.
DATA_DIR = join(expanduser('~'), '.local', 'share', 'pmcli')
# Location where we keep user and mpv configurations.
CONFIG_DIR = join(expanduser('~'), '.config', 'pmcli')
mc = Mobileclient()  # Our interface to Google Play Music.
q = songqueue.Queue()  # Queue/playlist.
w = writer.Writer(None, None, None, None, curses=False)  # Output handler.
v = view.View()  # Main window contents.
