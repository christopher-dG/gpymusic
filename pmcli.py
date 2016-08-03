from gmusicapi import Mobileclient

class Account:



    def __init__(self):
        self.api = Mobileclient()        
        logged_in = self.api.login('chrisadegraaf@gmail.com', 'GoogleMattAndChris', Mobileclient.FROM_MAC_ADDRESS)

        if logged_in == False:
            print("Login failed (exiting)")
            quit()
            
    def search(self, query, queryType):
        acceptedQueries = ['album', 'artist', 'song', 'playlist']
        if queryType in acceptedQueries:
            searchResult =  self.api.search(query, 10)[queryType+"_hits"]
        else:
            print("Unrecognized query type: choose from album, artist, song, playlist")
            searchResult = None
        return searchResult

# user  = Account()
# searchResult = user.search_album('21')
# print(searchResult[0].get('album'))



def search(query, queryType):
    acceptedQueries = ['album', 'artist', 'song']
    if queryType in acceptedQueries:
        results = user.search(query, queryType)
        if queryType == 'album':
            for result in results:
                print('Albums:')
                print(result['album']['artist'], ' - ', result['album']['name'])
        elif queryType == 'artist':
            print('Artists:')
            for result in results:
                print(result['artist']['name'])
        else:
            print('Songs:')
            for result in results:
                print(result['track']['artist'], ' - ', result['track']['title'], ' - ', result['track']['album'])


    else:
        print("Unrecognized query type: choose from album, artist, song, playlist")


user = Account()
search('forever', 'song')
