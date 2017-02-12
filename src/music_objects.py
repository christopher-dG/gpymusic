from api import api
import subprocess


def search(query, max_items=10):
    # searches google play for some user input
    print('Searching for %s:' % query.title())
    query_results = api.search(query, max_items)

    # returns a dict of lists with keys 'songs', 'artists', and 'albums'
    # each list has a maximum length of max_items
    return {
        'artists': [
            Artist(api.get_artist_info(
                artist['artist']['artistId'], max_top_tracks=max_items))
            for artist in query_results['artist_hits']
        ],
        'albums': [
            Album(api.get_album_info(
                album['album']['albumId']))
            for album in query_results['album_hits']],
        'songs': [
            Song(api.get_track_info(
                song['track']['storeId']))
            for song in query_results['song_hits']
        ]
    }


class MusicObject(dict):
    # Every MusicObject should at least have a name and id.
    def __init__(self, id, name, kind):
        self.__setitem__('id', id)
        self.__setitem__('name', name)
        self.__setitem__('kind', kind)

    def play(self, win):
        def to_string(song):
            return ' - '.join((song['name'], song['artist']))

        songs = [
            (self['id'], to_string(self))] if self['kind'] == 'song' else [
                (song['id'], to_string(song)) for song in self['songs']
            ]
        path = '~/.config/pmcli/mpv_input.conf'
        for id, string in songs:
            url = api.get_stream_url(id)
            win.erase()
            win.addstr('Now playing: %s' % string)
            win.refresh()
            if subprocess.call(
                    ['mpv', '--really-quiet', '--input-conf', path, url]
            ) is 11:
                break


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

    def collect(self, limit=None):
        items = {
            'songs': [
                Song(api.get_track_info(song['id']))
                for song in self['songs']
            ],
            'artists': [self],
            'albums': [
                Album(api.get_album_info(album['id']))
                for album in self['albums']
            ]
        }

        if limit is not None:
            for k in items.keys():
                items[k] = items[k][:limit]

        return items

    @staticmethod
    def show_fields(width):
        index_chars = 3
        count_chars = 7
        artist_chars = width - index_chars - 2*count_chars
        artist_start = 0 + index_chars
        album_count_start = artist_start + artist_chars
        song_count_start = album_count_start + count_chars
        song_offset = 3
        album_offset = 3
        return (index_chars, artist_chars, count_chars, artist_start,
                song_count_start, album_count_start, song_offset, album_offset)


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

    def collect(self, limit=None):
        items = {
            'songs': [
                Song(api.get_track_info(song['id']))
                for song in self['songs']
            ],
            # Artist IDs is already a list.
            'artists': [
                Artist(api.get_artist_info(id)) for id in self['artist_ids']
            ],
            'albums': [self]
        }

        if limit is not None:
            for k in items.keys():
                items[k] = items[k][:limit]

        return items

    @staticmethod
    def show_fields(width):
        index_chars = 3
        count_chars = 6
        album_chars = artist_chars = int((width - index_chars - count_chars)/2)
        total = sum([index_chars, count_chars, album_chars, artist_chars])
        if total != width:
            album_chars += width - total
        album_start = index_chars
        artist_start = album_start + album_chars
        song_count_start = artist_start + artist_chars
        song_offset = 2

        return (index_chars, album_chars, artist_chars, count_chars,
                album_start, artist_start, song_count_start, song_offset)


class Song(MusicObject):
    # Extra stuff: artist, album.
    def __init__(self, song):
        super().__init__(song['storeId'], song['title'], 'song')
        self.__setitem__('artist', song['artist'])
        self.__setitem__('artist_ids', song['artistId'])
        self.__setitem__('album', song['album'])
        self.__setitem__('album_id', song['albumId'])

    def collect(self, limit=None):
        items = {
            'songs': [self],
            'artists': [
                Artist(api.get_artist_info(id)) for id in self['artist_ids']
            ],
            'albums': [Album(api.get_album_info(self['album_id']))]
        }

        if limit is not None:
            for k in items.keys():
                items[k] = items[k][:limit]

        return items

    @staticmethod
    def show_fields(width):
        index_chars = 3
        title_chars = int((width - index_chars)/2)
        artist_chars = album_chars = int((width - index_chars)/4)
        total = sum([index_chars, title_chars, artist_chars, album_chars])
        if total != width:
            title_chars += width - total
        title_start = 0 + index_chars
        artist_start = title_start + title_chars
        album_start = artist_start + artist_chars
        return (index_chars, title_chars, artist_chars, album_chars,
                title_start, artist_start, album_start)
