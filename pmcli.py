from gmusicapi import Mobileclient
import abc, configparser, os, subprocess

class APIUser:
    def __init__(self):
        self.read_config()
        self.api = Mobileclient()
        logged_in = self.api.login(self.user_info['email'], self.user_info['password'], self.user_info['deviceid'])
        if not logged_in:
            print('Login failed (exiting).')
            quit()
        else:
            self.id = self.api.get_registered_devices()[0]['id']
            print('Logged in with device id ', self.id)

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
        self.user_info = {}
        for option in user_options:
            self.user_info[option] = config.get(user_section, option)

    def search(self, query):
        api_results = self.api.search(query, 3)
        results = {'artists': [], 'albums': [], 'songs': []} # wow look at me using dicts!
        for artist in api_results['artist_hits']:
            results['artists'].append(Artist(artist['artist']['name'], artist['artist']['artistId']))
        for album in api_results['album_hits']:
            results['albums'].append(Album(album['album']['artist'], album['album']['name'], album['album']['albumId']))
        for song in api_results['song_hits']:
            results['songs'].append(Song(song['track']['artist'], song['track']['album'], song['track']['title'], song['track']['storeId']))
        self.show_results(results)

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
        print('Playing')

    def show(self):
        print('stuff')

#------------------------------------------------------------
    
class Album(MusicObject):
    def __init__(self, artist, album, album_id):
        self.artist = artist
        self.album = album
        MusicObject.__init__(self, album_id)

    def to_string(self):
        return ' - '.join((self.artist, self.album))

    def play(self, shuffle=False):
        print('Playing')

    def show(self):
        print('Stuff')
    
        
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
        print('Playing')

    def show(self):
        print('Stuff')


if __name__ == '__main__':
    print('Welcome to (P)lay (M)usic for (CLI)!')
    user = APIUser()
    user.search("Rise Against")
