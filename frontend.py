import abc
import pmcli


class State(abc.ABC):
    @abc.abstractmethod
    def show(self):
        # displays whatever a state holds
        return


class ExpandableState(State):
    def __init__(self, options):
        self.options = options

    @abc.abstractclassmethod
    def length(self):
        # get the length of the list of options
        return

    @abc.abstractclassmethod
    def get_option(self, num):
        return


class SearchResultsState(ExpandableState):
    def __init__(self, search_results):
        super().__init__(search_results)

    def length(self):
        return sum([len(self.options[key]) for key in self.options])

    def show(self):
        i = 1
        for key in sorted(self.options):  # albums, artists, songs
            print('%s:' % key.capitalize())
            for result in self.options[key]:
                print('%d: %s' % (i, result.to_string()))
                i += 1

    def get_option(self, num):
        count = 1
        for key in sorted(self.options):
            for item in self.options[key]:
                if count is num:
                    return item
                else:
                    count += 1


class ShowObjectState(ExpandableState):
    def __init__(self, music_obj):
        super().__init__(music_obj)

    def length(self):  # get the length of all whatever list is being shown
        return self.options.length()

    def show(self):
        self.options.show()

    def get_option(self, num):
        count = 1
        if count is num:
            return self.options
        else:
            count += 1
            for key in self.options.contents:
                for item in self.options.contents[key]:
                    if count is num:
                        if item['id'].startswith('A'):
                            return pmcli.Artist(pmcli.API.api.get_artist_info(item['id']))
                        elif item['id'].startswith('B'):
                            return pmcli.Album(pmcli.API.api.get_album_info(item['id']))
                        elif item['id'].startswith('T'):
                            return pmcli.Song(pmcli.API.api.get_track_info(item['id']))
                    else:
                        count += 1

        # for key in sorted(self.options):
        #     for item in self.options[key]:
        #         if count is num:
        #             if item['id'].startswith('A'):
        #                 return pmcli.Artist(item['id'])
        #             elif item[key]['id'].startswith('B'):
        #                 return pmcli.Album(item['id'])
        #             elif item[key]['id'].startswith('T'):
        #                 return pmcli.Song(item['id'])
        #         else:
        #             count += 1


class HelpState(State):
    def show(self):
        print('Commands:')
        print('h/help: Show this help message')
        print('s/search search-term: Search for search-term')
        print('q/quit: Exit pmcli')
        print('p/play 123: Play item number 123')
        print('i/info 123: Show info on item number 123')


class InvalidInputState(State):
    def __init__(self, last_state):
        self.last_state = last_state

    def show(self):
        print('Invalid input: enter h for help')


def transition(current_state, user_input):
    # returns the new state
    user_input = [i.strip() for i in user_input.split(' ', 1)]

    # restore old state if we had invalid input
    if type(current_state).__name__ == 'InvalidInputState':
        current_state = current_state.last_state

    # search
    if user_input[0] == 's' or user_input[0] == 'search':
        next_state = SearchResultsState(api.search(user_input[1]))

    # play
    elif user_input[0] == 'p' or user_input[0] == 'play':
        if isinstance(current_state, ExpandableState):
            try:
                num = int(user_input[1])
                if num > current_state.length():
                    next_state = InvalidInputState(current_state)
                else:
                    current_state.get_option(num).play()
                    next_state = current_state
            except ValueError:
                next_state = InvalidInputState(current_state)
        else:
            next_state = InvalidInputState(current_state)

    # info
    elif user_input[0] == 'i' or user_input[0] == 'info':

        if isinstance(current_state, ExpandableState):  # sorry, python purists
            try:
                num = int(user_input[1])
                if num > current_state.length():
                    next_state = InvalidInputState(current_state)
                else:
                    next_state = ShowObjectState(current_state.get_option(num))
            except ValueError:
                next_state = InvalidInputState(current_state)
        else:
            next_state = InvalidInputState(current_state)

    # help
    elif user_input[0] == 'h' or user_input[0] == 'help':
        next_state = HelpState()

    # quit
    elif user_input[0] == 'q' or user_input[0] == 'quit':
        if input('Really quit? Enter q again to exit: ') == 'q':
            quit()
        next_state = current_state
    else:
        next_state = InvalidInputState(current_state)

    return next_state


if __name__ == '__main__':
    api = pmcli.API()
    print('Welcome to pmcli! Enter h for help.')
    state = None
    while True:
        state = transition(state, input('> '))
        if state:
            state.show()
