import curses as crs
from api import api, login
from music_objects import Song, Artist, Album


def get_input():
    inbar.addstr('> ')
    try:
        input = inbar.getstr()
    except KeyboardInterrupt:
        crs.endwin()
        quit()
    inbar.deleteln()
    return input.decode('utf-8')


def help(arg=None):
    main.erase()
    main.addstr(
        """Commands:
        s/search search-term: Search for search-term
        e/expand 123: Expand item number 123
        p/play 123: Play item number 123
        p/play q: Play current queue
        q/quit: Exit pmcli
        h/help: Show this help message
        """)
    return None


def search(query=None):
    if query is None:
        invalid(msg='Missing search query.')
        return None

    # Fetch as many results as we can display.
    limit = int((crs.LINES - 6)/3)
    outbar.erase()
    outbar.addstr('Searching for \'%s\'...' % query)
    outbar.refresh()
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

    outbar.erase()
    outbar.addstr('Enter \'e #\' or \'p #\' to expand or play an item.')

    return parsed


def get_option(num, content):
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


def expand(num=-1, content=None):
    if num == -1 or content is None:
        invalid(msg='Missing argument to play.')
        return None
    try:
        num = int(num)
    except ValueError:
        invalid(msg='Invalid argument to play.')
        return None
    opt = get_option(num, content)
    if opt is None:
        invalid(msg='Invalid number. Valid between 1-%d' %
                sum([len(content[k]) for k in content.keys()]))
        return None

    outbar.erase()
    outbar.addstr('Loading \'%s\'...' % opt['name'])
    outbar.refresh()

    content = opt.collect(limit=int(main.getmaxyx()[0]/2))
    return content


def show_queue():
    pl = {'song': [], 'artist': [], 'album': []}
    for item in playlist:
        pl[item['kind']].append(item)
    for key in pl.keys():
        pl[key + 's'] = pl.pop(key)
    return pl


def play(arg=-1, content=None):
    if arg == -1 or content is None:
        invalid(msg='Missing argument to play.')
        return None
    try:
        num = int(arg)
    except ValueError:
        if arg == 'q':
            for item in playlist:
                item.play(player)
                return content
        else:
            invalid(msg='Invalid argument to play.')
            return None
    except TypeError:
        invalid(msg='Missing argument to play.')
    opt = get_option(num, content)
    if opt is None:
        invalid(msg='Invalid number. Valid between 1-%d' %
                sum([len(content[k]) for k in content.keys()]))
        return None
    opt.play(player)
    return content


def invalid(msg=None):
    outbar.erase()
    outbar.addstr(
        'Error: ' + (msg if msg else '') +
        ' Enter h or help for help.'
    )


def queue(arg=-1, content=None):
    if arg in ('s', 'show'):
        content = show_queue()
        return content
    elif content is None:
        invalid(msg='Missing argument to play.')
        return None
    try:
        num = int(arg)
    except ValueError:
        invalid(msg='Invalid argument to play.')
        return None
    opt = get_option(num, content)
    if opt is None:
        invalid(msg='Invalid number. Valid between 1-%d' %
                sum([len(content[k]) for k in content.keys()]))
        return None
    outbar.erase()
    outbar.addstr('Added \'%s\' to queue.' % opt['name'])
    playlist.append(opt)
    return content


def transition(input, content):
    outbar.erase()
    outbar.addstr(input)

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
        if commands[command] in (play, expand, queue):
            content = commands[command](arg, content)
        else:
            content = commands[command](arg)
        if content is not None:
            main.erase()
            display(content)
    else:
        invalid(msg='Nonexistent command.')

    refresh()
    return content


def trunc(string, chars):
    if chars < 0 or len(string) <= chars:
        return string
    else:
        return string[:-((len(string) - chars) + 3)] + '...'


def display(content):
    width = main.getmaxyx()[1]

    (index_chars, title_chars, artist_chars, album_chars,
     title_start, artist_start, album_start) = Song.show_fields(width)

    main.erase()
    y, i = 0, 1

    if content['songs']:
        main.addstr(y, 0, '#')
        main.addstr(y, title_start, trunc('Title', title_chars))
        main.addstr(y, artist_start, trunc('Artist', artist_chars))
        main.addstr(y, album_start, trunc('Album', album_chars))
        y += 1
    for song in content['songs']:
        main.addstr(y, 0, str(i).zfill(2))
        main.addstr(y, title_start, trunc(song['name'], title_chars))
        main.addstr(y, artist_start, trunc(song['artist'], artist_chars))
        main.addstr(y, album_start, trunc(song['album'], album_chars))
        y += 1
        i += 1

    (index_chars, artist_chars, count_chars, artist_start, song_count_start,
     album_count_start, song_offset, album_offset) = Artist.show_fields(width)

    if content['artists']:
        main.addstr(y, 0, '#')
        main.addstr(y, artist_start, trunc('Artist', artist_chars))
        main.addstr(y, song_count_start, trunc(' Songs', count_chars))
        main.addstr(y, album_count_start, trunc('Albums', count_chars))
        y += 1
    for artist in content['artists']:
        main.addstr(y, 0, str(i).zfill(2))
        main.addstr(y, title_start, trunc(artist['name'], artist_chars))
        main.addstr(
            y, song_count_start+song_offset,
            str(len((artist['songs']))).zfill(2)
        )
        main.addstr(
            y, album_count_start+album_offset,
            str(len((artist['albums']))).zfill(2)
        )
        y += 1
        i += 1

    (index_chars, album_chars, artist_chars, count_chars, album_start,
     artist_start, song_count_start, song_offset) = Album.show_fields(width)

    if content['albums']:
        main.addstr(y, 0, '#')
        main.addstr(y, album_start, trunc('Album', album_chars))
        main.addstr(y, artist_start, trunc('Artist', artist_chars))
        main.addstr(y, song_count_start, trunc('Songs', count_chars))
        y += 1
    for album in content['albums']:
        main.addstr(y, 0, str(i).zfill(2))
        main.addstr(y, title_start, trunc(album['name'], album_chars))
        main.addstr(y, artist_start, trunc(album['artist'], artist_chars))
        main.addstr(
            y, song_count_start+song_offset, str(len(album['songs'])).zfill(2)
        )
        y += 1
        i += 1


def refresh():
    [win.refresh() for win in (main, outbar, player, inbar)]


if __name__ == '__main__':
    main = crs.initscr()  # For the bulk of output.
    inbar = crs.newwin(1, crs.COLS, crs.LINES-1, 0)  # For user input.
    player = crs.newwin(1, crs.COLS, crs.LINES-2, 0)  # For 'now playing'.
    outbar = crs.newwin(1, crs.COLS, crs.LINES-3, 0)  # For hints and notices.
    main.addstr(5, int(crs.COLS/2) - 9, 'Welcome to pmcli!')
    outbar.addstr('Enter \'h\' or \'help\' if you need help.')
    player.addstr('Logged in as ' + login())
    refresh()
    content = None
    playlist = []
    while True:
        content = transition(get_input(), content)
