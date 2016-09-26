import abc
import api_user
import subprocess


class MusicObject(abc.ABC):  # albums, artists, and songs are represented as MusicObjects
    def __init__(self, name, id):
        self.name = name  # name of the item
        self.id = id  # a unique ID

    @abc.abstractmethod
    def length(self):  # return the summed length of all of an item's sublists + itself
        pass

    @abc.abstractmethod
    def play(self):  # stream the item
        pass

    @abc.abstractmethod
    def show(self):  # print the item's formatted info
        pass

    @abc.abstractmethod
    def to_string(self):  # return formatted info on the item
        pass


# ------------------------------------------------------------

class Artist(MusicObject):
    def __init__(self, artist):  # artist is a dict from Mobileclient.get_artist_info
        self.contents = {}  # the artist's albums and songs
        # some ugly checks because some artists don't have albums and/or songs
        if 'albums' in artist:
            # make this a list even though it's only one item to make other methods simpler
            self.contents['albums'] = [{'name': album['name'], 'id': album['albumId']} for album in artist['albums']]
        else:
            self.contents['albums'] = []
        if 'topTracks' in artist:
            self.contents['songs'] = [{'name': song['title'], 'id': song['storeId']} for song in artist['topTracks']]
        else:
            self.contents['songs'] = []
        super().__init__(artist['name'], artist['artistId'])

    def length(self):  # return number of albums and songs and itself
        return sum([len(self.contents[key]) for key in self.contents]) + 1

    def to_string(self):  # return the name
        return self.name

    def play(self):  # play top tracks
        for song in self.contents['songs']:
            url = api_user.API.get_stream_url(song['id'])
            print('Playing %s:' % (' - '.join((self.name, song['name']))))
            # we set the exit code for 'q' to 11 in our custom input.conf
            if subprocess.call(['mpv', '--really-quiet', '--input-conf=~/.config/pmcli/mpv_input.conf', url]) is 11:
                break

    def show(self):  # print artist name, then list of albums, then list of songs
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
    def __init__(self, album):  # album is a dict from Mobileclient.get_album_info
        # contents: the album's artist and songs
        self.contents = {'artist': [{'name': album['artist'], 'id': album['artistId'][0]}],
                         'songs': [{'name': song['title'], 'id': song['storeId']} for song in album['tracks']]}
        super().__init__(album['name'], album['albumId'])

    def length(self):  # return number of songs and artist + itself
        return len(self.contents['songs']) + 2

    def to_string(self):  # return artist - album
        return ' - '.join((self.contents['artist'][0]['name'], self.name))

    def play(self):  # play the album's songs
        for song in self.contents['songs']:
            url = api_user.API.get_stream_url(song['id'])
            print('Playing %s:' % (' - '.join((self.contents['artist'][0]['name'], song['name'], self.name))))
            # we set the exit code for 'q' to 11 in our custom input.conf
            if subprocess.call(['mpv', '--really-quiet', '--input-conf=~/.config/pmcli/mpv_input.conf', url]) is 11:
                break

    def show(self):  # print the album name, then list of songs
        i = 1
        print('%d: %s' % (i, self.to_string()))
        i += 1
        print('Artist:')
        print('%d: %s' % (i, self.contents['artist'][0]['name']))
        i += 1
        print('Songs:')
        for song in self.contents['songs']:
            print('%d: %s' % (i, song['name']))
            i += 1


# ------------------------------------------------------------

class Song(MusicObject):
    def __init__(self, song):  # song is a dict from Mobileclient.get_track_info
        # contents: the song's artist and album
        self.contents = {'artist': {'name': song['artist'], 'id': song['artistId'][0]},
                         'album': {'name': song['album'], 'id': song['albumId']}}
        super().__init__(song['title'], song['storeId'])

    def length(self):  # always return 1
        return 1

    def to_string(self):  # return artist - song - album
        return ' - '.join((self.contents['artist']['name'], self.name, self.contents['album']['name']))

    def play(self):  # play the song
        url = api_user.API.get_stream_url(self.id)
        print('Playing %s:' % self.to_string())
        subprocess.call(['mpv', '--really-quiet', url])

    def show(self):  # print the foratted song info
        print('1: %s' % (self.to_string()))
