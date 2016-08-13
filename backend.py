from gmusicapi import Mobileclient
from random import shuffle
import abc, configparser, os, subprocess

class API:

    api = Mobileclient()
    id = ''
    
    def __init__(self):
        user_info = self.read_config()
        logged_in = API.api.login(user_info['email'], user_info['password'], user_info['deviceid'])
        if not logged_in:
            print('Login failed (exiting).')
            quit()
        else:
            API.id = API.api.get_registered_devices()[0]['id']
            print('Logged in with device id ', API.id)

    def read_config(self, path=None):
        if not path:
            path = os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'config')
        config = configparser.ConfigParser()
        if not os.path.isfile(path):
            print('Config file not found at ', path, '(exiting).')
            quit()
        config.read(path)
        if not 'User' in config.sections():
            print('Section \'[User]\' not found in ', path, '. See config.example (exiting).')
            quit()
        user_section = config.sections()[0]
        user_options = config.options(user_section)
        user_info = {}
        for option in user_options:
            user_info[option] = config.get(user_section, option)
        return user_info
            
    def search(self, query):
        api_results = API.api.search(query, 3)
        results = {'songs': [], 'artists': [], 'albums': []} # wow look at me using dicts!
        for artist in api_results['artist_hits']:
            results['artists'].append(Artist(artist['artist']['name'], artist['artist']['artistId']))
        for album in api_results['album_hits']:
            results['albums'].append(Album(album['album']['artist'], album['album']['name'], album['album']['albumId']))
        for song in api_results['song_hits']:
            results['songs'].append(Song(song['track']['artist'], song['track']['album'], song['track']['title'], song['track']['storeId']))
        self.show_results(results)
        return results

    def show_results(self, results):
        count = 1
        for key in results:
            if len(results[key]) > 0:
                print(key.capitalize(), ':')
                for i in results[key]:
                    print(count, ': ', i.to_string())
                    count += 1

#------------------------------------------------------------            

class MusicObject(abc.ABC):
    def __init__(self, obj_id):
        self.obj_id = obj_id

    @abc.abstractmethod
    def to_string():
        return

    @abc.abstractmethod
    def play():
        return

    @abc.abstractmethod
    def show():
        return
    
#------------------------------------------------------------            

class Artist(MusicObject):
    def __init__(self, artist, artist_id):
        self.artist = artist
        MusicObject.__init__(self, artist_id)

    def to_string(self):
        return self.artist
        
    def play(self, shuffle=False):
        api_results = API.api.get_artist_info(self.obj_id, True, 5, 0)
        urls = []
        print('Getting stream URLs for ', self.to_string(), ':')
        for song in api_results['topTracks']:
            urls.append(API.api.get_stream_url(song['storeId']))
        if shuffle:
            shuffle(urls)
        playlist = open(os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'playlist'), 'w')
        for url in urls:
            playlist.write("%s\n" % url)
        playlist.close()
        print('Playing ', self.to_string(), ':')
        subprocess.call(['mpv', '-playlist', os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'playlist')])
        

    def show(self):
        api_results = API.api.get_artist_info(self.obj_id, True, 15, 0)
        artist = {'songs': [], 'albums': []}
        songs = []
        for song in api_results['topTracks']:
            artist['songs'].append(Song(song['artist'], song['album'], song['title'], song['storeId']))
        for album in api_results['albums']:
            artist['albums'].append(Album(album['artist'], album['name'], album['albumId']))
        count = 1
        for key in artist:
            print(key.capitalize(), ':')
            for i in artist[key]:
                print(count, ': ', i.to_string())
                count += 1

#------------------------------------------------------------
    
class Album(MusicObject):
    def __init__(self, artist, album, album_id):
        self.artist = artist
        self.album = album
        MusicObject.__init__(self, album_id)

    def to_string(self):
        return ' - '.join((self.artist, self.album))

    def play(self, shuffle=False):
        api_results = API.api.get_album_info(self.obj_id)
        urls = []
        print('Getting stream URLs for ', self.to_string(), ':')
        for song in api_results['tracks']:
            urls.append(API.api.get_stream_url(song['storeId']))
        if shuffle:
            shuffle(urls)
        playlist = open(os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'playlist'), 'w')
        for url in urls:
            playlist.write("%s\n" % url)
        playlist.close()
        print('Playing ', self.to_string(), ':')
        subprocess.call(['mpv', '-playlist', os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'playlist')])

    def show(self):
        api_results = API.api.get_album_info(self.obj_id)
        songs = []
        for song in api_results['tracks']:
            songs.append(Song(song['artist'], song['album'], song['title'], song['storeId']))
        count = 1
        for song in songs:
            print(count, ': ', song.to_string())
            count += 1
        
#------------------------------------------------------------
    
class Song(MusicObject):

    def __init__(self, artist, album, song, song_id):
        self.artist = artist
        self.album = album
        self.song = song
        MusicObject.__init__(self, song_id)

    def to_string(self):
        return ' - '.join((self.artist, self.song, self.album))
    
    def play(self):
        print('Getting stream URL:')
        url = API.api.get_stream_url(self.obj_id)
        print('Playing ', self.to_string(), ':')
        subprocess.call(['mpv', '-really-quiet', url])
        
    def show(self):
        print(self.to_string())
