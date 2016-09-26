#!/usr/bin/python
import api_user
import states

MAX_ITEMS = 10  # maximum number of api search results of each type


def transition(current_state, user_input):  # takes the user input and generates the next state
    user_input = [i.strip().lower() for i in user_input.split(' ', 1)]  # command - the rest
    if isinstance(current_state, states.NoChangeState):  # restore old state if we had invalid input
        current_state = current_state.last_state
    # search
    if user_input[0] == 's' or user_input[0] == 'search':
        next_state = states.SearchResultsState(api_user.APIUser.search(user_input[1], MAX_ITEMS))
    # info
    elif user_input[0] == 'i' or user_input[0] == 'info':
        if isinstance(current_state, states.ExpandableState):
            try:
                num = int(user_input[1])
                if num > current_state.length() or num <= 0:
                    next_state = states.InvalidInputState(current_state)
                else:  # valid input
                    next_state = states.ShowObjectState(current_state.get_option(num))
            except ValueError:
                next_state = states.InvalidInputState(current_state)
        else:
            next_state = states.InvalidInputState(current_state)
    # play
    elif user_input[0] == 'p' or user_input[0] == 'play':
        if isinstance(current_state, states.ExpandableState):  # sorry, python purists
            try:
                num = int(user_input[1])
                if num > current_state.length() or num <= 0:
                    next_state = states.InvalidInputState(current_state)
                else:  # valid input
                    current_state.get_option(num).play()
                    next_state = current_state
            except ValueError:
                next_state = states.InvalidInputState(current_state)
        else:
            next_state = states.InvalidInputState(current_state)
    # help
    elif user_input[0] == 'h' or user_input[0] == 'help':
        next_state = states.HelpState(current_state)
    # quit
    elif user_input[0] == 'q' or user_input[0] == 'quit':
        if input('Really quit? Enter q again to exit: ') == 'q':
            quit()
        next_state = current_state
    else:
        next_state = states.InvalidInputState(current_state)
    return next_state  # returns the new state


if __name__ == '__main__':
    api = api_user.APIUser.login()
    print('Welcome to pmcli! Enter h for help.')
    state = None
    while True:
        state = transition(state, input('> '))
        if state:
            state.show()
