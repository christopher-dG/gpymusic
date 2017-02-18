import curses as crs
from api import api, login
from music_objects import Song, Artist, Album, Playlist
from util import (
    addstr, to_string, leave, measure_fields, trunc, error_msg
)


def expand(num=None):
    """
    Display all of a MusicObject's information: songs, artists, and albums.

    Keyword arguments:
    num=None: Index of the MusicObject in the main window to be expanded.
    """
    global content
    if num is None:
        error_msg(outbar, 'Missing argument to play.')
    elif content is None:
        error_msg(outbar, 'Wrong context for expand.')
    else:
        try:
            num = int(num)
        except ValueError:
            error_msg(outbar, 'Invalid argument to play.')
        else:
            limit = int((main.getmaxyx()[0] - 6)/3)
            opt = get_option(num, limit)
            if opt is not None:
                addstr(outbar, 'Loading \'%s\'...' % to_string(opt))
                content = opt.collect(limit=limit)
                outbar.erase()
                outbar.refresh()
            else:
                error_msg(outbar, 'Invalid number. Valid between 1-%d.' %
                          sum([len(content[k]) for k in content.keys()]))


def help(arg=0):
    """
    Display basic pmcli commands.

    Keyword arguments:
    arg=0: Irrelevant.
    """
    # Don't use generic addstr() because we don't want to call trunc() here.
    main.erase()
    main.addstr(
        """
        Commands:
        s/search search-term: Search for search-term
        e/expand 123: Expand item number 123
        p/play: Play current queue
        p/play 123: Play item number 123
        q/queue: Show current queue
        q/queue 123:  Add item number 123 to queue
        h/help: Show this help message
        Ctrl-C: Exit pmcli
        """
    )
    main.refresh()


# Todo: deal with properly displaying shuffled playlists.
def play(arg=None):
    """
    Play a MusicObject or the current queue.

    Keyword arguments:
    arg=None: A number n to play item n, 's' to play the queue in shuffle mode,
      or None to play the current queue in order.
    """
    global content
    if arg is None or arg is 's':
        pl = playlist.collect()
        if pl is None:
            error_msg(outbar, 'The queue is empty.')
        else:
            content = pl
            display()
            addstr(outbar, '[spc] pause [q] stop [n] next [9-0] volume')
            playlist.play(infobar, s=arg is 's')
            outbar.erase()
            outbar.refresh()
    elif content is None:
        error_msg(outbar, 'Wrong context for play.')
    else:
        try:
            num = int(arg)
        except ValueError:
            error_msg(outbar, 'Invalid argument to play.')
        else:
            opt = get_option(num)
            if opt is not None:
                addstr(outbar, '[spc] pause [q] stop [n] next [9-0] volume')
                opt.play(infobar)
                addstr(infobar, 'Now playing: None')
                outbar.erase()
                outbar.refresh()
            else:
                error_msg(outbar, 'Invalid number. Valid between 1-%d' %
                          sum([len(content[k]) for k in content.keys()]))


def queue(num=None):
    """
    Display the current queue, or add an item to the queue.

    Keyword arguments:
    num=None: Index of the MusicObject in the main window to add to
      the queue, or None to display the queue.
    """
    global content

    if num is None:
        pl = playlist.collect()
        if pl is None:
            error_msg(outbar, 'The queue is empty.')
        else:
            content = pl
    elif content is None:
        error_msg(outbar, 'Wrong context for queue.')

    else:
        try:
            num = int(num)
        except ValueError:
            error_msg(outbar, 'Invalid argument to queue.')
        else:
            opt = get_option(num)

            if opt is not None:
                if opt['kind'] == 'artist':
                    error_msg(
                        outbar, 'Can only add songs or albums to the queue.')
                elif opt['id'] in playlist.ids:
                    error_msg(outbar, '\'%s\' is already in the queue.' %
                              to_string(opt))
                else:
                    if opt['kind'] == 'album':
                        playlist.extend(Song(api.get_track_info(
                            song['id'])) for song in opt['songs'])
                        playlist.ids.extend(
                            song['id'] for song in opt['songs'])
                    else:
                        playlist.append(opt)
                    playlist.ids.append(opt['id'])
                    addstr(outbar, 'Added \'%s\' to queue.' %
                           to_string(opt))
            else:
                error_msg(outbar, 'Invalid number. Valid between 1-%d.' %
                          sum([len(content[k]) for k in content.keys()]))


def search(query):
    """
    Search Google Play Music for a given query .

    Arguments:
    query: The search query.

    Returns: A dict of lists with keys 'songs', 'artists', and 'albums'.
    """
    global content
    if query is None:
        error_msg(outbar, 'Missing search query.')

    # Fetch as many results as we can display.
    limit = int((main.getmaxyx()[0] - 3)/3)
    addstr(outbar, 'Searching for \'%s\'...' % query)
    result = api.search(query, max_results=limit)
    outbar.erase()
    outbar.refresh()

    mapping = {
        'songs': {
            'class': Song,
            'hits': 'song_hits',
            'key': 'track',
        },
        'artists': {
            'class': Artist,
            'hits': 'artist_hits',
            'key': 'artist',
        },
        'albums': {
            'class': Album,
            'hits': 'album_hits',
            'key': 'album',
        }
    }
    content = {'songs': [], 'artists': [], 'albums': []}
    for k in content.keys():
        result[k] = iter(result[mapping[k]['hits']])

    # Basically just create 'limit' of each type.

    for i in range(limit):
        for k in content.keys():
            try:
                content[k].append(
                    mapping[k]['class'](next(result[k])[mapping[k]['key']])
                )
            except StopIteration:
                pass

    return content


def display():
    """Update the main window with some content."""
    main.erase()
    y, i = 0, 1
    (index_chars, name_chars, artist_chars, album_chars, name_start,
     artist_start, album_start) = measure_fields(main.getmaxyx()[1])

    if 'songs' in content and content['songs']:
        main.addstr(y, 0, '#', crs.A_UNDERLINE)
        main.addstr(y, name_start, trunc('Title', name_chars),
                    crs.A_UNDERLINE)
        main.addstr(y, artist_start, trunc('Artist', artist_chars),
                    crs.A_UNDERLINE)
        main.addstr(y, album_start, trunc('Album', album_chars),
                    crs.A_UNDERLINE)
        y += 1
        for song in content['songs']:
            main.addstr(y, 0, str(i).zfill(2))
            main.addstr(y, name_start, trunc(song['name'], name_chars))
            main.addstr(y, artist_start, trunc(song['artist'], artist_chars))
            main.addstr(y, album_start, trunc(song['album'], album_chars))
            y += 1
            i += 1

    if 'artists' in content and content['artists']:
        main.addstr(y, 0, '#', crs.A_UNDERLINE)
        main.addstr(y, name_start, trunc('Artist', name_chars),
                    crs.A_UNDERLINE)
        y += 1
        for artist in content['artists']:
            main.addstr(y, 0, str(i).zfill(2))
            main.addstr(y, name_start, trunc(artist['name'], name_chars))
            y += 1
            i += 1

    if 'albums' in content and content['albums']:
        main.addstr(y, 0, '#', crs.A_UNDERLINE)
        main.addstr(y, name_start, trunc('Album', name_chars),
                    crs.A_UNDERLINE)
        main.addstr(y, artist_start, trunc('Artist', artist_chars),
                    crs.A_UNDERLINE)
        y += 1
        for album in content['albums']:
            main.addstr(y, 0, str(i).zfill(2))
            main.addstr(y, name_start, trunc(album['name'], name_chars))
            main.addstr(y, artist_start, trunc(album['artist'], artist_chars))
            y += 1
            i += 1

    main.refresh()


def get_option(num, limit=-1):
    """
    Select a numbered MusicObject from the main window

    Arguments:
    num: Index of the MusicObject in the main window to be returned.

    Keyword argumnents:
    limit=-1: Number of songs to generate for artists,
      determined by terminal height.

    Returns: The MusicObject at index 'num'.
    """
    if num < 0 or num > sum([len(content[k]) for k in content.keys()]):
        return None
    i = 1
    for key in ('songs', 'artists', 'albums'):  # Hardcoded to guarantee order.
        for item in content[key]:
            if i == num:
                return item.fill(limit)
            else:
                i += 1
    return None


def get_input():
    """Get user input in the bottom bar."""
    addstr(inbar, '> ')
    crs.curs_set(2)
    try:
        input = inbar.getstr()
    except KeyboardInterrupt:
        addstr(outbar, 'Goodbye, thanks for using pmcli!')
        leave(1)
    inbar.deleteln()
    crs.curs_set(0)
    return input.decode('utf-8')


def transition(input):
    """
    Route input to the appropriate function.

    Arguments:
    input: User input.
    """
    commands = {
        'h': help,
        'help': help,
        'e': expand,
        'expand': expand,
        's': search,
        'search': search,
        'p': play,
        'play': play,
        'q': queue,
        'queue': queue
    }

    arg = None
    if content is None:
        addstr(infobar, 'Now playing: None')
    try:
        command, arg = input.split(' ', 1)
    except ValueError:
        command = input

    if command in commands:
        commands[command](arg)
        if content is not None:
            display()
    else:
        error_msg(outbar, 'Nonexistent command.')


if __name__ == '__main__':
    main = crs.initscr()  # For the bulk of output.
    main.resize(crs.LINES-3, crs.COLS)
    inbar = crs.newwin(1, crs.COLS, crs.LINES-1, 0)  # For user input.
    infobar = crs.newwin(1, crs.COLS, crs.LINES-2, 0)  # For 'now playing'.
    outbar = crs.newwin(1, crs.COLS, crs.LINES-3, 0)  # For hints and notices.
    main.addstr(5, int(crs.COLS/2) - 9, 'Welcome to pmcli!')
    main.refresh()
    crs.curs_set(0)
    addstr(outbar, 'Logging in...')
    login(outbar)
    addstr(infobar, 'Enter \'h\' or \'help\' if you need help.')
    playlist = Playlist()
    global content
    content = None
    while True:
        transition(get_input())
