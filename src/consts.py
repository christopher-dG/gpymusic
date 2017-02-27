from gmusicapi import Mobileclient
from os.path import expanduser, join
import music_objects
import writer
import songqueue
import view

DATA_DIR = join(expanduser('~'), '.local', 'share', 'pmcli')
CONFIG_DIR = join(expanduser('~'), '.config', 'pmcli')
l = None  # Later to be filled in with library.Library()
mc = Mobileclient()
q = songqueue.Queue()
w = writer.Writer(None, None, None, None, curses=False)
v = view.View()


"""
Music object mapping:
cls: Class name of each type.
hits: Key in mc.search() results.
rslt_key: Key in an individual entry from mc.search()
lookup: method to retrieve object information
"""
mapping = {
    'songs': {
        'cls': music_objects.Song,
        'hits': 'song_hits',
        'rslt_key': 'track',
        'lookup': mc.get_track_info,
    },
    'artists': {
        'cls': music_objects.Artist,
        'hits': 'artist_hits',
        'rslt_key': 'artist',
        'lookup': mc.get_artist_info,
    },
    'albums': {
        'cls': music_objects.Album,
        'hits': 'album_hits',
        'rslt_key': 'album',
        'lookup': mc.get_album_info,
    },
    'libsongs': {
        'cls': music_objects.LibrarySong,
        'hits': '',
        'rslt_key': '',
        'lookup': '',
    },
}
