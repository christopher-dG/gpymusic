from api import api
from subprocess import call
from util import to_string, addstr, time_from_ms
from random import shuffle


class MusicObject(dict):
    """A dict representing a song, artist, or album."""
    def __init__(self, id, name, kind, full):
        """
        MusicObject contstructor.

        Arguments:
        id: Unique item id as determined by gmusicapi.
        name: Title of song/album or name of artist.
        kind: Type of object: song, artist, or album.
        full: Whether or not the item contains all possible information.
          MusicObjects generated from search() results are not full,
          MusicObjects generated from get_{track|artist|album_info}() are full.
        """
        self.__setitem__('id', id)
        self.__setitem__('name', name)
        self.__setitem__('kind', kind)
        self.__setitem__('full', full)

    @staticmethod
    def play(win, songs):
        """
        Play some songs.

        Arguments:
        win: Window on which to display song information.
        songs: List of songs to play. Songs are tuples following the
          format (song_string, song_id, song_length).

        Returns: None if all items were played, or the index of the
          first unplayed item to be used in restoring the queue.
        """
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
    """A dict representing an artist."""
    def __init__(self, artist, full=False):
        """
        Artist constructor.

        Arguments:
        artist: Dict with artist information from gmusicapi.

        Keyword arguments:
        full=False: Whether or not the artist's song list is populated.
        """
        super().__init__(artist['artistId'], artist['name'], 'artist', full)
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

    def fill(self, limit):
        """
        If an Artist is not full, fill in its song list.

        Arguments:
        limit: The number of songs to generate, determined by terminal height.

        Returns: A new, full, Artist
        """
        if self['full']:
            return self
        self = Artist(api.get_artist_info(
            self['id'], max_top_tracks=limit), full=True)
        return self

    def play(self, win):
        """
        Play an Artist's song list.

        Arguments:
        win: Window on which to display song information.
        """
        MusicObject.play(
            win, [(song['id'], to_string(song), song['time'])
                  for song in self['songs']]
        )

    def collect(self, limit=20):
        """
        Collect all of an Artist's information: songs, artist, and albums.

        Keyword arguments:
        limit=20: Upper limit of each element to collect,
          determined by terminal height.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
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
    """A dict representing an album."""
    def __init__(self, album, full=False):
        """
        Album constructor.

        Arguments:
        artist: Dict with album information from gmusicapi.

        Keyword arguments:
        full=False: Whether or not the album's song list is populated.
        """
        super().__init__(album['albumId'], album['name'], 'album', full)
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

    def fill(self, limit=0):
        """
        If an Album is not full, fill in its song list.

        Arguments:
        limit: Irrelevant, we always generate all songs.

        Returns: A new, full, Album
        """
        if self['full']:
            return self
        self = Album(api.get_album_info(self['id']), full=True)
        return self

    def play(self, win):
        """
        Play an Album's song list.

        Arguments:
        win: Window on which to display song information.
        """
        MusicObject.play(
            win, [(song['id'], to_string(song), song['time'])
                  for song in self['songs']]
        )

    def collect(self, limit=20):
        """
        Collect all of an Album's information: songs, artist, and albums.

        Keyword arguments:
        limit=20: Upper limit of each element to collect,
          determined by terminal height.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
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
    """A dict representing a song."""
    def __init__(self, song, full=True):
        """
        Song constructor.

        Arguments:
        song: Dict with song information from gmusicapi.

        Keyword arguments:
        full=True: A song is always considered full.
        """
        super().__init__(song['storeId'], song['title'], 'song', full)
        self.__setitem__('artist', song['artist'])
        self.__setitem__('artist_ids', song['artistId'])
        self.__setitem__('album', song['album'])
        self.__setitem__('album_id', song['albumId'])
        self.__setitem__('time', time_from_ms(int(song['durationMillis'])))

    def fill(self, limit=0):
        """All songs are already full."""
        return self

    def play(self, win):
        """
        Play an Song.

        Arguments:
        win: Window on which to display song information.
        """
        MusicObject.play(win, [(self['id'], to_string(self), self['time'])])

    def collect(self, limit=None):
        """
        Collect all of a Song's information: songs, artist, and albums.

        Keyword arguments:
        limit=None: Irrelevant.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
        return {
            'songs': [self],
            'artists': [
                Artist(api.get_artist_info(id)) for id in self['artist_ids']
            ],
            'albums': [Album(api.get_album_info(self['album_id']))]
        }


class Playlist(list):
    """A queue of songs to be played."""
    def __init__(self):
        """Playlist constructor."""
        super().__init__(self)
        self.ids = []

    def play(self, win, s=False):
        """
        Play a playlist.

        Arguments:
        win: Window on which to display song information.
        s=False: Whether or not the playlist is shuffled.

        Returns: None if the playlist is empty.
        """
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
        if not s and index is not None:
            for item in cache[index:]:
                self.append(item)
                self.ids.append(item['id'])

    def collect(self, s=False):
        """
        Collect all of a Playlist's information: songs, artist, and albums.

        Keyword arguments:
        s=False: Whether or not the playlist is shuffled..

        Returns: A dict with key 'songs'.
        """
        songs = {'songs': [item for item in self]} if len(self) > 0 else None
        if s and songs is not None:
            shuffle(songs['songs'])
        return songs
