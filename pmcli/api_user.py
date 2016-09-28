from gmusicapi import Mobileclient
import music_objects
import os

API = Mobileclient()  # our interface to google music


class APIUser:  # we use this to interact with the MobileClient
    @staticmethod
    def login():  # log into google music
        user_info = APIUser.read_config()
        if not API.login(user_info['email'], user_info['password'], user_info['deviceid']):
            print('Login failed (exiting).')
            quit()
        print('Logged in as %s.' % user_info['email'])
        return API  # return the Mobileclient interface that we can now use anywhere

    @staticmethod
    def read_config():  # reads the config file to get login info
        config_path = os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'config')
        if not os.path.isfile(config_path):
            print('Config file not found at %s, (exiting).' % config_path)
            quit()
        user_info = {}
        with open(config_path, 'r') as config:
            for line in config:
                key_val = [i.strip() for i in line.split(':', 1)]
                user_info[key_val[0]] = key_val[1]
        return user_info  # returns a dict with keys 'email', 'password', and 'deviceid'

    @staticmethod
    # todo: allow user to specify max_items
    def search(query, max_items=10):  # searches google play for some user input
        print('Searching for %s:' % query.title())
        query_results = API.search(query, max_items)
        # returns a dict of lists with keys 'songs', 'artists', and 'albums'
        # each list has a maximu length of max_items
        return {'artists': [music_objects.Artist(API.get_artist_info(artist['artist']['artistId'], max_top_tracks=max_items))
                            for artist in query_results['artist_hits']],
                'albums': [music_objects.Album(API.get_album_info(album['album']['albumId'])) for album in
                           query_results['album_hits']],
                'songs': [music_objects.Song(API.get_track_info(song['track']['storeId'])) for song in
                          query_results['song_hits']]}
