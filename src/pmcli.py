import curses as crs
from api import api, login
from music_objects import Song, Artist, Album, Playlist
from util import addstr, to_string, leave, measure_fields


def get_input():
    addstr(inbar, '> ')
    try:
        input = inbar.getstr()
    except KeyboardInterrupt:
        addstr(outbar, 'Goodbye, thanks for using pmcli!')
        leave(1)
    inbar.deleteln()
    return input.decode('utf-8')


def help(arg=0):
    addstr(
        main,
        """Commands:
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
    return None, None


def search(query):
    if query is None:
        invalid('Missing search query.')
        return None, None

    # Fetch as many results as we can display.
    limit = int((main.getmaxyx()[0] - 6)/3)
    addstr(outbar, 'Searching for \'%s\'...' % query)
    result = api.search(query, max_results=limit)

    # Creating MusicObjects is expensive, so only create as many as we need
    # while still maintaining the desired number of search results.
    # The smaller the terminal, the faster this goes. :^)
    # Note: I am absolutely not going to remember how this works tomorrow.

    mapping = {
        'songs': {
            'class': Song,
            'hits': 'song_hits',
            'key': 'track',
            'info': api.get_track_info,
            'id': 'storeId'
        },
        'artists': {
            'class': Artist,
            'hits': 'artist_hits',
            'key': 'artist',
            'info': api.get_artist_info,
            'id': 'artistId'
        },
        'albums': {
            'class': Album,
            'hits': 'album_hits',
            'key': 'album',
            'info': api.get_album_info,
            'id': 'albumId'
        }
    }
    parsed = {'songs': [], 'artists': [], 'albums': []}
    for k in parsed.keys():
        result[k] = iter(result[mapping[k]['hits']])

    # Basically just create 'limit' of each type.

    for i in range(limit):
        for k in parsed.keys():
            try:
                parsed[k].append(
                    mapping[k]['class'](mapping[k]['info'](
                        next(result[k])[mapping[k]['key']][mapping[k]['id']]
                    ))
                )
            except StopIteration:
                pass

    return parsed, None


def get_option(num):
    if num < 0 or num > sum([len(content[k]) for k in content.keys()]):
        return None
    i = 1
    for key in ('songs', 'artists', 'albums'):  # Hardcoded to guarantee order.
        for item in content[key]:
            if i == num:
                return item
            else:
                i += 1
    return None


def expand(num):
    if num == -1 or content is None:
        invalid('Missing argument to play.')
        return None, None
    try:
        num = int(num)
    except ValueError:
        invalid('Invalid argument to play.')
        return None, None
    opt = get_option(num)
    if opt is None:
        invalid('Invalid number. Valid between 1-%d' %
                sum([len(content[k]) for k in content.keys()]))
        return None, None

    addstr(outbar, 'Loading \'%s\'...' % to_string(opt))

    return opt.collect(limit=int((main.getmaxyx()[0] - 6)/3)), None


def play_queue():
    if playlist.play(player) is None:
        invalid('Queue is empty.')


def play(arg):
    if arg is None:
        play_queue()
        return content, None
    elif content is None:
        invalid('Wrong context for play.')
        return content, None
    try:
        num = int(arg)
    except ValueError:
        invalid('Invalid argument to play.')
        return content, None
    except TypeError:
        invalid('Missing argument to play.')
        return content, None

    opt = get_option(num)
    if opt is None:
        invalid('Invalid number. Valid between 1-%d' %
                sum([len(content[k]) for k in content.keys()]))
    else:
        opt.play(player)

    return content, None


def invalid(msg):
    addstr(outbar, 'Error: ' + msg + ' Enter \'h\' or \'help\' for help.')


def queue(arg):
    out = None
    if arg is None:
        q = playlist.collect()
        if list(q.values()) == [[], [], []]:
            invalid('Nothing in the queue.')
            return content, out
        return q, out
    elif content is None:
        invalid('Wrong context for queue.')
        return content, out
    try:
        num = int(arg)
    except ValueError:
        invalid(msg='Invalid argument to play.')
        return content, out

    opt = get_option(num)
    addstr(main, to_string(opt))
    if opt is None:
        invalid(msg='Invalid number. Valid between 1-%d' %
                sum([len(content[k]) for k in content.keys()]))
    else:
        playlist.append(opt)
        out = 'Added \'%s\' to queue.' % to_string(opt)

    return content, out


def transition(input, content):
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
    try:
        command, arg = input.split(' ', 1)
    except ValueError:
        command = input

    # Todo: make this less ugly.
    if command in commands:
        content, out = commands[command](arg)
        if content is not None:
            if out is not None:
                display(content, out)
            else:
                display(content)
    else:
        invalid('Nonexistent command.')

    return content,


def trunc(string, chars):
    if chars < 0 or len(string) <= chars:
        return string
    else:
        return string[:-((len(string) - chars) + 3)] + '...'


def display(content, out=None):
    if out is not None:
        outbar.addstr(out)
    main.erase()
    y, i = 0, 1
    (index_chars, name_chars, artist_chars, album_chars, count_chars,
     name_start, artist_start, album_start, song_count_start,
     album_count_start, offset) = measure_fields(main.getmaxyx()[1])

    if content['songs']:
        main.addstr(y, 0, '#')
        main.addstr(y, name_start, trunc('Title', name_chars))
        main.addstr(y, artist_start, trunc('Artist', artist_chars))
        main.addstr(y, album_start, trunc('Album', album_chars))
        y += 1
    for song in content['songs']:
        main.addstr(y, 0, str(i).zfill(2))
        main.addstr(y, name_start, trunc(song['name'], name_chars))
        main.addstr(y, artist_start, trunc(song['artist'], artist_chars))
        main.addstr(y, album_start, trunc(song['album'], album_chars))
        y += 1
        i += 1

    if content['artists']:
        main.addstr(y, 0, '#')
        main.addstr(y, name_start, trunc('Artist', name_chars))
        main.addstr(y, song_count_start, trunc(' Songs', count_chars))
        main.addstr(y, album_count_start, trunc('Albums', count_chars))
        y += 1
    for artist in content['artists']:
        main.addstr(y, 0, str(i).zfill(2))
        main.addstr(y, name_start, trunc(artist['name'], name_chars))
        main.addstr(
            y, song_count_start + offset,
            str(len((artist['songs']))).zfill(2)
        )
        main.addstr(
            y, album_count_start + offset,
            str(len((artist['albums']))).zfill(2)
        )
        y += 1
        i += 1

    if content['albums']:
        main.addstr(y, 0, '#')
        main.addstr(y, name_start, trunc('Album', name_chars))
        main.addstr(y, artist_start, trunc('Artist', artist_chars))
        main.addstr(y, song_count_start, trunc(' Songs', count_chars))
        y += 1
    for album in content['albums']:
        main.addstr(y, 0, str(i).zfill(2))
        main.addstr(y, name_start, trunc(album['name'], name_chars))
        main.addstr(y, artist_start, trunc(album['artist'], artist_chars))
        main.addstr(
            y, song_count_start + offset, str(len(album['songs'])).zfill(2)
        )
        y += 1
        i += 1

    main.refresh()


if __name__ == '__main__':
    main = crs.initscr()  # For the bulk of output.
    inbar = crs.newwin(1, crs.COLS, crs.LINES-1, 0)  # For user input.
    player = crs.newwin(1, crs.COLS, crs.LINES-2, 0)  # For 'now playing'.
    outbar = crs.newwin(1, crs.COLS, crs.LINES-3, 0)  # For hints and notices.
    main.addstr(5, int(crs.COLS/2) - 9, 'Welcome to pmcli!')
    main.refresh()
    addstr(outbar, 'Logging in...')
    login(outbar)
    addstr(player, 'Enter \'h\' or \'help\' if you need help.')
    content = None
    playlist = Playlist()
    while True:
        content = transition(get_input(), content)
