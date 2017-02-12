from api import api
from subprocess import call
from util import to_string, addstr
from random import shuffle


class MusicObject(dict):
    # Every MusicObject should at least have a name, id, and kind.
    def __init__(self, id, name, kind):
        self.__setitem__('id', id)
        self.__setitem__('name', name)
        self.__setitem__('kind', kind)

    @staticmethod
    def play(win, items):
        path = '~/.config/pmcli/mpv_input.conf'
        for i in range(len(items)):
            url = api.get_stream_url(items[i][0])
            addstr(win, 'Now playing: %s' % items[i][1])
            if call(
                    ['mpv', '--really-quiet', '--input-conf', path, url]
            ) is 11:
                return items[i:]
        return None


class Artist(MusicObject):
    # Extra stuff: songs, albums.
    def __init__(self, artist):
        super().__init__(artist['artistId'], artist['name'], 'artist')
        self.__setitem__('id', artist['artistId'])
        self.__setitem__('name', artist['name'])
        try:
            self.__setitem__('songs', [
                {
                    'name': song['title'],
                    'artist': song['artist'],
                    'album': song['album'],
                    'id': song['storeId']
                } for song in artist['topTracks']
            ])
        except KeyError:
            self.__setitem__('songs', [])
        try:
            self.__setitem__('albums', [
                {
                    'name': album['name'],
                    'artist': album['artist'],
                    'id': album['albumId']
                } for album in artist['albums']
            ])
        except KeyError:
            self.__setitem__('albums', [])

    def play(self, win):
        MusicObject.play(
            win, [(item['id'], to_string(item)) for item in self['songs']]
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
            aggregate['songs'].append(
                Song(api.get_track_info(next(songs))['id'])

            )
            aggregate['albums'].append(
                Album(api.get_album_info(next(albums))['id'])
            )

        return aggregate


class Album(MusicObject):
    # Extra stuff: artist, songs.
    def __init__(self, album):
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
                    'id': song['storeId']
                } for song in album['tracks']
            ])
        except KeyError:
            self.__setitem__('songs', [])

    def play(self, win):
        MusicObject.play(
            win, [(item['id'], to_string(item)) for item in self['songs']]
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
            aggregate['songs'].append(
                Song(api.get_track_info(next(songs))['id'])

            )

        return aggregate


class Song(MusicObject):
    # Extra stuff: artist, album.
    def __init__(self, song):
        super().__init__(song['storeId'], song['title'], 'song')
        self.__setitem__('artist', song['artist'])
        self.__setitem__('artist_ids', song['artistId'])
        self.__setitem__('album', song['album'])
        self.__setitem__('album_id', song['albumId'])

    def play(self, win):
        MusicObject.play(win, [(self['id'], to_string(self))])

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

    def play(self, win, s=False):
        if list(self.collect().values()) == [[], [], []]:
            return None
        items = [(item['id'], to_string(item)) for item in self]
        if s:
            shuffle(items)
        del self[:]

        remainder = MusicObject.play(win, items)
        if remainder is not None:
            for item in remainder:
                self.append(item)

    def collect(self):
        aggregate = {'songs': [], 'artists': [], 'albums': []}
        for item in self:
            aggregate[item['kind'] + 's'].append(item)

        return aggregate
