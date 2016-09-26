import abc
import os
import subprocess

from gmusicapi import Mobileclient


class API: # we use this to interact with the MobileClient
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
        config_path = os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'config')
        if not os.path.isfile(config_path):
            print('Config file not found at %s, (exiting).' % config_path)
            quit()
        user_info = {}
        with open(config_path, 'r') as config:
            for line in config:
                key_val = [i.strip() for i in line.split(':', 1)]
                user_info[key_val[0]] = key_val[1]
        return user_info

    @staticmethod
    def search(query):
        print('Searching for %s:' % query)
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
    def __init__(self, name, id):
        self.name = name
        self.id = id

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
        self.contents = {}
        if 'albums' in artist:
            self.contents['albums'] = [{'name': album['name'], 'id': album['albumId']} for album in artist['albums']]
        else:
            self.contents['albums'] = {}
        if 'topTracks' in artist:
            self.contents['songs'] = [{'name': song['title'], 'id': song['storeId']} for song in artist['topTracks']]
        else:
            self.contents['songs'] = {}
        super().__init__(artist['name'], artist['artistId'])

    def length(self):
        return sum([len(self.contents[key]) for key in self.contents])

    def to_string(self):
        return self.name

    def play(self):
        for song in self.contents['songs']:
            url = API.api.get_stream_url(song['id'])
            print('Playing %s:' % (' - '.join((self.name, song['name']))))
            if subprocess.call(['mpv', '--really-quiet', '--input-conf=~/.config/pmcli/mpv_input.conf', url]) is 11:
                break

    def show(self):
        i = 1
        print('%d: %s' % (i, self.to_string()))
        i += 1
        print('Albums:')
        for album in self.contents['albums']:
            print('%d: %s' % (i, album['name']))
            i += 1
        print('Songs:')
        for song in self.contents['songs']:
            print('%d: %s' % (i, song['name']))
            i += 1


# ------------------------------------------------------------

class Album(MusicObject):
    def __init__(self, album):
        self.contents = {}
        self.contents = {'artist': {'name': album['artist'], 'id': album['artistId']},
                         'songs': [{'name': song['title'], 'id': song['storeId']} for song in album['tracks']]}
        super().__init__(album['name'], album['albumId'])

    def length(self):
        return len(self.contents['songs'])

    def to_string(self):
        return ' - '.join((self.contents['artist']['name'], self.name))

    def play(self):
        for song in self.contents['songs']:
            url = API.api.get_stream_url(song['id'])
            print('Playing %s:' % (' - '.join((self.contents['artist']['name'], song['name'], self.name))))
            if subprocess.call(['mpv', '--really-quiet', '--input-conf=~/.config/pmcli/mpv_input.conf', url]) is 11:
                break

    def show(self):
        i = 1
        print(self.to_string())
        i += 1
        print('Songs:')
        for song in self.contents['songs']:
            print('%d: %s' % (i, song['name']))
            i += 1


# ------------------------------------------------------------

class Song(MusicObject):
    def __init__(self, song):
        self.contents = {'artist': {'name': song['artist'], 'id': song['artistId'][0]},
                         'album': {'name': song['album'], 'id': song['albumId']}}
        super().__init__(song['title'], song['storeId'])

    def length(self):
        return 1

    def to_string(self):
        return ' - '.join((self.contents['artist']['name'], self.name, self.contents['album']['name']))

    def play(self):
        print('Getting stream URL:')
        url = API.api.get_stream_url(self.id)
        print('Playing %s:' % self.to_string())
        subprocess.call(['mpv', '--really-quiet', url])

    def show(self):
        print('1: %s' % (self.to_string()))
