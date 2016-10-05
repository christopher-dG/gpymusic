import abc
import api_user
import music_objects


class State(abc.ABC):  # states hold info on where we are in the program
    @abc.abstractmethod
    def show(self):  # displays relevant info from the current state
        pass

# ------------------------------------------------------------


class ExpandableState(State):  # ExpandableStates have lists that we can interact with
    def __init__(self, content):  # content is either a dict MusicObjects or a MusicObject
        self.content = content

    @abc.abstractclassmethod
    def get_option(self, num):  # return the appropriate MusicObject by matching  an inputted number to a list entry
        pass

    @abc.abstractclassmethod
    def length(self):  # get the length of the list of options
        pass

    @abc.abstractmethod
    def show(self):
        pass

# ------------------------------------------------------------


class NoChangeState(State):  # NoChangeStates are states that have no affect on our position in the program
    def __init__(self, last_state):  # last_state is the state that will be later restored
        self.last_state = last_state

    @abc.abstractmethod
    def show(self):
        pass

# ------------------------------------------------------------


class SearchResultsState(ExpandableState):
    def __init__(self, search_results):  # search_results is a dict of MusicObjects from Mobileclient.search
        super().__init__(search_results)

    def length(self):  # return number of search_results
        return sum([len(self.content[key]) for key in self.content])

    def show(self):  # print search results
        i = 1
        for key in sorted(self.content):  # albums, artists, songs
            print('%s:' % key.capitalize())
            for item in self.content[key]:
                print('%d: %s' % (i, item.to_string()))
                i += 1

    def get_option(self, num):  # return the num-th search result
        i = 1
        for key in sorted(self.content):
            for item in self.content[key]:
                if i is num:
                    return item
                else:
                    i += 1

# ------------------------------------------------------------


class ShowObjectState(ExpandableState):
    def __init__(self, music_obj):  # music_obj is a MusicObject
        super().__init__(music_obj)

    def length(self):  # get the length of all whatever list is being shown
        return self.content.length()

    def show(self):  # display the MusicObject
        self.content.show()

    def get_option(self, num):  # return the num-th entry in music_object's combined sublists
        i = 1
        if i is num:
            return self.content  # first entry is the MusicObject itself
        else:
            i += 1
            for key in sorted(self.content.contents):
                for item in self.content.contents[key]:
                    if i is num:
                        # artist IDs start with A, albums with B, and songs with T
                        # we need to create a new MusicObject because item only holds the name + id
                        if item['id'].startswith('A'):
                            return music_objects.Artist(api_user.API.get_artist_info(item['id']))
                        elif item['id'].startswith('B'):
                            return music_objects.Album(api_user.API.get_album_info(item['id']))
                        elif item['id'].startswith('T'):
                            return music_objects.Song(api_user.API.get_track_info(item['id']))
                    else:
                        i += 1

# ------------------------------------------------------------


class HelpState(NoChangeState):
    def __init__(self, last_state):
        super().__init__(last_state)

    def show(self):
        print('Commands:')
        print('s/search search-term: Search for search-term')
        print('i/info 123: Show info on item number 123')
        print('p/play 123: Play item number 123')
        print('q/quit: Exit pmcli')
        print('h/help: Show this help message')
        
# ------------------------------------------------------------


class InvalidInputState(NoChangeState):
    def __init__(self, last_state):
        super().__init__(last_state)

    def show(self):
        print('Invalid input: enter h for help')
