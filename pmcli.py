import abc
import os
import subprocess

from gmusicapi import Mobileclient


class API:
    api = Mobileclient()

    def __init__(self):
        # logs into the API
        user_info = self.read_config()
        logged_in = API.api.login(user_info['email'], user_info['password'], user_info['deviceid'])
        if not logged_in:
            print('Login failed (exiting).')
            quit()
        print('Logged in with device id %s' % user_info['deviceid'])

    @staticmethod
    def read_config():
        # reads the config file to get login info
        # returns a dict with keys 'email', 'password', and 'deviceid'
        path = os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'config')
        if not os.path.isfile(path):
            print('Config file not found at %s, (exiting).' % path)
            quit()
        user_info = {}
        with open(path, 'r') as config:
            for line in config:
                key_val = [i.strip() for i in line.split(':', 1)]
                user_info[key_val[0]] = key_val[1]
        return user_info

    @staticmethod
    def search(query):
        print('Searching for %s' % query)
        # searches google play for some user input
        # returns a dict with keys 'songs', 'artists', and 'albums' (each value is a list)
        query_results = API.api.search(query, 10)
        return {'artists': [Artist(API.api.get_artist_info(artist['artist']['artistId'])) for artist in
                            query_results['artist_hits']],
                'albums': [Album(API.api.get_album_info(album['album']['albumId'])) for album in
                           query_results['album_hits']],
                'songs': [Song(API.api.get_track_info(song['track']['storeId'])) for song in
                          query_results['song_hits']]}


# ------------------------------------------------------------

class MusicObject(abc.ABC):
    def __init__(self, obj_id):
        self.obj_id = obj_id

    @abc.abstractmethod
    def length(self):
        # returns the number of a MusicObjects child objects, for example number of songs in an Album
        return

    @abc.abstractmethod
    def append_ids(self):
        # combines all child object ids into one list, for example all the songs in an album
        return

    @abc.abstractmethod
    def to_string(self):
        # returns formatted info on the MusicObject
        return

    @abc.abstractmethod
    def play(self):
        # streams the MusicObject
        return

    @abc.abstractmethod
    def show(self):
        # prints a the MusicObject's formatted info
        return


# ------------------------------------------------------------

class Artist(MusicObject):
    def __init__(self, artist):
        self.contents = {'name': artist['name'],
                         'albums_ids': [album['albumId'] for album in artist['albums']],
                         'albums': [album['name'] for album in artist['albums']],
                         'song_ids': [song['storeId'] for song in artist['topTracks']],
                         'songs': [song['title'] for song in artist['topTracks']]}
        super().__init__(artist['artistId'])

    def length(self):
        return len(self.contents['albums']) + len(self.contents['songs'])

    def append_ids(self):
        return self.contents['album_ids'] + self.contents['song_ids']

    def to_string(self):
        return self.contents['name']

    def play(self):
        urls = []
        print('Getting stream URLs for %s:' % self.to_string())
        urls = [API.api.get_stream_url(song_id) for song_id in self.contents['song_ids']]
        with open(os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'playlist'), 'w') as playlist:
            for url in urls:
                playlist.write("%s\n" % url)
        print('Playing %s:' % self.to_string())
        subprocess.call(['mpv', '-playlist', os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'playlist')])

    def show(self):
        count = 1
        print(self.to_string())
        print('Songs:')
        for song in self.contents['songs']:
            print('%d: %s' % (count, song.capitalize()))
            count += 1
        print('Albums:')
        for album in self.contents['albums']:
            print('%d: %s' % (count, album.capitalize()))
            count += 1


# ------------------------------------------------------------

class Album(MusicObject):
    def __init__(self, album):
        self.contents = {'name': album['name'],
                         'artist': album['artist'],
                         'artist_id': album['artistId'],
                         'songs': [song['title'] for song in album['tracks']],
                         'song_ids': [song['storeId'] for song in album['tracks']]}
        super().__init__(album['albumId'])

    def length(self):
        return len(self.contents['songs'])

    def append_ids(self):
        return [self.obj_id] + [self.contents['artist_id']] + self.contents['song_ids']

    def to_string(self):
        return ' - '.join((self.contents['artist'], self.contents['name']))

    def play(self):
        print('Getting stream URLS for %s:' % self.to_string())
        urls = [API.api.get_stream_url(song_id) for song_id in self.contents['song_ids']]
        playlist = open(os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'playlist'), 'w')
        for url in urls:
            playlist.write("%s\n" % url)
        playlist.close()
        print('Playing %s:' % self.to_string())
        subprocess.call(['mpv', '-playlist', os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'playlist')])

    def show(self):
        count = 1
        print('%d: %s' % (count, self.to_string()))
        count += 1
        print('Songs:')
        for song in self.contents['songs']:
            print('%d: %s' % (count, song.capitalize()))
            count += 1


# ------------------------------------------------------------

class Song(MusicObject):
    def __init__(self, song):
        self.contents = {'name': song['title'],
                         'artist_id': song['artistId'][0],
                         'artist': song['artist'],
                         'album_id': song['album'],
                         'album': song['album']}
        super().__init__(song['storeId'])

    def length(self):
        return 1

    def append_ids(self):
        return self.obj_id

    def to_string(self):
        return ' - '.join((self.contents['artist'], self.contents['name'], self.contents['album']))

    def play(self):
        print('Getting stream URL:')
        url = API.api.get_stream_url(self.obj_id)
        print('Playing %s:' % self.to_string())
        subprocess.call(['mpv', '-really-quiet', url])

    def show(self):
        count = 1
        print('%d: %s' % self.to_string())
