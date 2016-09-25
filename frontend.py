import abc
import pmcli


class State(abc.ABC):
    @abc.abstractmethod
    def show(self):
        # displays whatever a state holds
        return


class SearchResultsState(State):
    def __init__(self, search_results):
        self.search_results = search_results

    def length(self):
        return sum([len(self.search_results[key]) for key in self.search_results])

    def show(self):
        i = 1
        for key in self.search_results:
            print('%s:' % key.capitalize())
            for result in self.search_results[key]:
                print('%d: %s' % (i, result.to_string()))
                i += 1


class ShowObjectState(State):
    def __init__(self, music_obj):
        self.music_obj = music_obj

    def length(self):  # get the length of all whatever list is being shown
        return self.music_obj.length()

    def show(self):
        self.music_obj.show()


class HelpState(State):
    def __init__(self):
        pass

    def show(self):
        print('Commands:')
        print('h/help: Show this help message')
        print('s/search search-term: Search for search-term')
        print('q/quit: Exit pmcli')
        print('p/play 123: Play item number 123')
        print('i/info 123: Show info on item number 123')


class InvalidInputState(State):
    def __init__(self):
        pass

    def show(self):
        print('Invalid input: enter h for help')


def transition(current_state, user_input):
    # returns the new state
    play_states = info_states = ['ShowObjectState',
                                 'SearchResultsState']  # only allow play/info commands at these states
    user_input = [i.strip() for i in user_input.split(' ', 1)]

    # search
    if user_input[0] == 's' or user_input[0] == 'search':
        next_state = SearchResultsState(api.search(user_input[1]))

    # play
    elif user_input[0] == 'p' or user_input[0] == 'play':
        if type(current_state).__name__ in play_states:
            try:
                num = int(user_input[1])

            except ValueError:
                next_state = InvalidInputState()
        else:
            next_state = InvalidInputState()

    # info
    elif user_input[0] == 'i' or user_input[0] == 'info':
        if type(current_state).__name__ in info_states:
            try:
                num = int(user_input[1])
                if num > current_state.length():
                    next_state = InvalidInputState()
                else:
                    pass

            except ValueError:
                next_state = InvalidInputState()
        else:
            next_state = InvalidInputState()

    # help
    elif user_input[0] == 'h' or user_input[0] == 'help':
        next_state = HelpState()

    # quit
    elif user_input[0] == 'q' or user_input[0] == 'quit':
        if input('Really quit? Enter q again to exit: ') == 'q':
            quit()
        next_state = current_state
    else:
        next_state = InvalidInputState()

    return next_state

# def get_list_entry(current_state, num):

if __name__ == '__main__':
    api = pmcli.API()
    print('Welcome to pmcli!')
    state = None
    while True:
        state = transition(state, input('> '))
        if state:
            state.show()
