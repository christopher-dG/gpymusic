import os

import music_objects
from gmusicapi import Mobileclient

API = Mobileclient()


class APIUser:  # we use this to interact with the MobileClient
    @staticmethod
    def login():
        user_info = APIUser.read_config()
        if not API.login(user_info['email'], user_info['password'], user_info['deviceid']):
            print('Login failed (exiting).')
            quit()
        print('Logged in with device id %s' % user_info['deviceid'])
        return API

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
        print('Searching for %s' % query)
        # searches google play for some user input
        # returns a dict with keys 'songs', 'artists', and 'albums' (each value is a list)
        query_results = API.search(query, 10)
        return {'artists': [music_objects.Artist(API.get_artist_info(artist['artist']['artistId'])) for artist in
                            query_results['artist_hits']],
                'albums': [music_objects.Album(API.get_album_info(album['album']['albumId'])) for album in
                           query_results['album_hits']],
                'songs': [music_objects.Song(API.get_track_info(song['track']['storeId'])) for song in
                          query_results['song_hits']]}