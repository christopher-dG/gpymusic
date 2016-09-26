import abc

import utils
from pmcli import api


class State(abc.ABC):
    @abc.abstractmethod
    def show(self):
        # displays relevant info from the current state
        pass


class ExpandableState(State):
    def __init__(self, content):
        self.content = content

    @abc.abstractclassmethod
    def get_option(self, num):
        pass

    @abc.abstractclassmethod
    def length(self):  # get the length of the list of options
        pass

    def show(self):
        pass


class NoChangeState(State):

    def __init__(self, last_state):
        self.last_state = last_state

    def show(self):
        pass


class SearchResultsState(ExpandableState):
    def __init__(self, search_results):
        super().__init__(search_results)

    def length(self):
        return sum([len(self.content[key]) for key in self.content])

    def show(self):
        i = 1
        for key in sorted(self.content):  # albums, artists, songs
            print('%s:' % key.capitalize())
            for result in self.content[key]:
                print('%d: %s' % (i, result.to_string()))
                i += 1

    def get_option(self, num):
        i = 1
        for key in sorted(self.content):
            for item in self.content[key]:
                if i is num:
                    return item
                else:
                    i += 1


class ShowObjectState(ExpandableState):
    def __init__(self, music_obj):
        super().__init__(music_obj)

    def length(self):  # get the length of all whatever list is being shown
        return self.content.length()

    def show(self):
        self.content.show()

    def get_option(self, num):
        i = 1
        if i is num:
            return self.content
        else:
            i += 1
            for key in sorted(self.content.contents):
                for item in self.content.contents[key]:
                    if i is num:
                        if item['id'].startswith('A'):
                            return utils.Artist(api.get_artist_info(item['id']))
                        elif item['id'].startswith('B'):
                            return utils.Album(api.get_album_info(item['id']))
                        elif item['id'].startswith('T'):
                            return utils.Song(api.get_track_info(item['id']))
                    else:
                        i += 1


class HelpState(NoChangeState):
    def __init__(self, last_state):
        super().__init__(last_state)

    def show(self):
        print('Commands:')
        print('h/help: Show this help message')
        print('s/search search-term: Search for search-term')
        print('q/quit: Exit pmcli')
        print('p/play 123: Play item number 123')
        print('i/info 123: Show info on item number 123')


class InvalidInputState(NoChangeState):
    def __init__(self, last_state):
        super().__init__(last_state)

    def show(self):
        print('Invalid input: enter h for help')


