from api import api
from subprocess import call
from util import to_string, addstr, time_from_ms
from random import shuffle


class MusicObject(dict):
    # Every MusicObject should at least have a name, id, and kind.
    def __init__(self, id, name, kind):
        self.__setitem__('id', id)
        self.__setitem__('name', name)
        self.__setitem__('kind', kind)

    @staticmethod
    def play(win, songs):
        # Iterable of items follows the format (id, song string, song length).
        path = '~/.config/pmcli/mpv_input.conf'
        i = 1
        for song in songs:
            url = api.get_stream_url(song[0])
            addstr(win, 'Now playing: %s (%s)' %
                   (song[1], song[2]))
            if call(
                    ['mpv', '--really-quiet', '--input-conf', path, url]
            ) is 11:  # 'q' returns this exit code.
                return i if i < len(songs) else None
            i += 1
        return None


class Artist(MusicObject):
    # Extra stuff: songs, albums.
    def __init__(self, artist, full=False):
        super().__init__(artist['artistId'], artist['name'], 'artist')
        self.__setitem__('id', artist['artistId'])
        self.__setitem__('name', artist['name'])
        try:
            self.__setitem__('songs', [
                {
                    'name': song['title'],
                    'artist': song['artist'],
                    'album': song['album'],
                    'id': song['storeId'],
                    'time': time_from_ms(int(song['durationMillis'])),
                    'kind': 'song'
                } for song in artist['topTracks']
            ])
        except KeyError:
            self.__setitem__('songs', [])
        try:
            self.__setitem__('albums', [
                {
                    'name': album['name'],
                    'artist': album['artist'],
                    'id': album['albumId'],
                    'kind': 'album'
                } for album in artist['albums']
            ])
        except KeyError:
            self.__setitem__('albums', [])
        # 'full' artists come from get_artist_info, they have lists of
        # albums and songs.
        self.__setitem__('full', full)

    def fill(self, limit):  # Add songs and albums.
        if self['full']:
            return self
        self = Artist(api.get_artist_info(
            self['id'], max_top_tracks=limit), full=True)
        return self

    def play(self, win):
        MusicObject.play(
            win, [(song['id'], to_string(song), song['time'])
                  for song in self['songs']]
        )

    def collect(self, limit=20):
        aggregate = {
            'songs': [],
            'artists': [self],
            'albums': []
        }

        songs = iter(self['songs'])
        albums = iter(self['albums'])
        for i in range(limit):
            try:
                aggregate['songs'].append(
                    Song(api.get_track_info(next(songs)['id']))
                )
            except StopIteration:
                pass
            try:
                aggregate['albums'].append(
                    Album(api.get_album_info(next(albums)['id']))
                )
            except StopIteration:
                pass

        return aggregate


class Album(MusicObject):
    # Extra stuff: artist, songs.
    def __init__(self, album, full=False):
        super().__init__(album['albumId'], album['name'], 'album')
        self.__setitem__('artist', album['artist'])
        self.__setitem__('artist_ids', album['artistId'])
        try:
            self.__setitem__('songs', [
                {
                    'name': song['title'],
                    'artist': song['artist'],
                    'artist_id': song['artistId'][0],
                    'album': song['album'],
                    'id': song['storeId'],
                    'time': time_from_ms(int(song['durationMillis'])),
                    'kind': 'song'
                } for song in album['tracks']
            ])
        except KeyError:
            self.__setitem__('songs', [])
        # 'full' albums come from api.get_album_info(),
        # they have lists of songs.
        self.__setitem__('full', full)

    def fill(self, limit=0):  # Get list of songs.
        if self['full']:
            return self
        self = Album(api.get_album_info(self['id']), full=True)
        return self

    def play(self, win):
        MusicObject.play(
            win, [(song['id'], to_string(song), song['time'])
                  for song in self['songs']]
        )

    def collect(self, limit=20):
        aggregate = {
            'songs': [],
            'artists': [
                Artist(api.get_artist_info(id)) for id in self['artist_ids']
            ],
            'albums': [self],
        }

        songs = iter(self['songs'])
        for i in range(limit):
            try:
                aggregate['songs'].append(
                    Song(api.get_track_info(next(songs)['id']))
                )
            except StopIteration:
                pass

        return aggregate


class Song(MusicObject):
    # Extra stuff: artist, album.
    def __init__(self, song, full=True):
        super().__init__(song['storeId'], song['title'], 'song')
        self.__setitem__('artist', song['artist'])
        self.__setitem__('artist_ids', song['artistId'])
        self.__setitem__('album', song['album'])
        self.__setitem__('album_id', song['albumId'])
        self.__setitem__('time', time_from_ms(int(song['durationMillis'])))
        # Search results come with all the info we need, so songs
        # are 'full' by default.
        self.__setitem__('full', full)

    def fill(self, limit=0):  # Songs are full by default.
        return self

    def play(self, win):
        MusicObject.play(win, [(self['id'], to_string(self), self['time'])])

    def collect(self, limit=None):
        return {
            'songs': [self],
            'artists': [
                Artist(api.get_artist_info(id)) for id in self['artist_ids']
            ],
            'albums': [Album(api.get_album_info(self['album_id']))]
        }


class Playlist(list):
    def __init__(self):
        super().__init__(self)
        self.ids = []

    def play(self, win, s=False):
        if not self.collect()['songs']:
            return None

        songs = [(song['id'], to_string(song), song['time']) for song in self]
        if s:
            shuffle(songs)

        # Save the queue contents to restore unplayed items.
        cache = []
        for i in range(len(songs)):
            cache.append(self.pop(0))
        del self.ids[:]

        index = MusicObject.play(win, songs)
        addstr(win, 'Now playing: None')

        # I'll figure out how to make this work with shuffle later.
        if not s:
            if index is not None:
                for item in cache[index:]:
                    self.append(item)
                    self.ids.append(item['id'])

    def collect(self, s=False):
        songs = {'songs': [item for item in self]} if len(self) > 0 else None
        if s and songs is not None:
            shuffle(songs['songs'])
        return songs
