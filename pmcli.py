from gmusicapi import Mobileclient
import os
import subprocess
import configparser

class Account:

    def __init__(self, username, password, deviceId):
        self.api = Mobileclient()
        logged_in = self.api.login(username, password, deviceId)
        
        if logged_in == False:
            print("Login failed (exiting)")
            quit()
        else:
            self.id = self.api.get_registered_devices()[0]['id']
            
    def search(self, query, queryType):
        acceptedQueries = ['album', 'artist', 'song', 'playlist']
        if queryType in acceptedQueries:
            searchResult =  self.api.search(query, 10)
        else:
            print("Unrecognized query type: choose from album, artist, song, playlist")
            searchResult = None
        return searchResult

    def getUrl(self, storeId):
        return self.api.get_stream_url(storeId)

def readConfig():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser('~'), '.config', 'pmcli', 'config'))
    userSection = config.sections()[0]
    userOptions = config.options(userSection)
    userInfo = {}
    for option in userOptions:
        userInfo[option] = config.get(userSection, option)
    return userInfo


def search(query, queryType):

    # returns a list of tuples with format:
    # (artist, album) for albums
    # (artist) for artists
    # (artist, song, album) for songs
    
    acceptedQueries = ['album', 'artist', 'song']
    if queryType in acceptedQueries:
        results = []
        searchResults = user.search(query, queryType)[queryType+"_hits"]
        if queryType == 'album':
            for result in searchResults:
                results.append((result['album']['artist'], result['album']['name'], result['album']['albumId']))
        elif queryType == 'artist':
            for result in searchResults:
                results.append((result['artist']['name'], result['artist']['artistId']))
        else:
            print('Songs:')
            for result in searchResults:
                results.append((result['track']['artist'], result['track']['title'], result['track']['album'], result['track']['storeId']))
    else:
        print("Unrecognized query type: choose from album, artist, song, playlist")
        results = None
        
    return results

# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    userInfo = readConfig()
    user = Account(userInfo['email'], userInfo['password'], userInfo['deviceid'])
    results = search('forever', 'song')
    # count = 1
    # for result in results:
    #     print(count, ': ', ' - '.join(result))
    #     print(user.getUrl(result[-1]))
    subprocess.call(['mplayer', '-quiet', user.getUrl(results[0][-1])])
