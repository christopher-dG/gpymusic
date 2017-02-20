#!/usr/bin/env python3

import curses as crs
from gmusicapi import Mobileclient
from os.path import exists, expanduser, join, isfile
from random import shuffle
import json
import warnings

warnings.filterwarnings('ignore')

api = Mobileclient()  # Our interface to Google Music.


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
        'q': enqueue,
        'queue': enqueue,
        'w': write,
        'write': write,
        'r': restore,
        'restore': restore,
    }

    arg = None
    if content is None:
        addstr(infobar, 'Now playing: None')

    try:
        command, arg = input.split(maxsplit=1)

    except ValueError:
        command = input

    if command in commands:
        commands[command](arg)
        if content is not None:
            display()

    else:
        error_msg(outbar, 'Nonexistent command.')


def get_input():
    """Get user input in the bottom bar."""
    addstr(inbar, '> ')
    crs.curs_set(2)  # Show the cursor.

    try:
        input = inbar.getstr()

    except KeyboardInterrupt:
        addstr(outbar, 'Goodbye, thanks for using pmcli!')
        leave(1)

    inbar.deleteln()
    crs.curs_set(0)  # Hide the cursor.

    return input.decode('utf-8')


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
        return None  # num out of range.
    i = 1

    for key in ('songs', 'artists', 'albums'):  # Hardcoded to guarantee order.
        for item in content[key]:
            if i == num:
                return item.fill(limit)  # Always return item with all content.
            else:
                i += 1

    return None


def display():
    """Update the main window with some content."""
    main.erase()
    y, i = 0, 1  # y coordinate in main window, current item index.
    (index_chars, name_chars, artist_chars, album_chars, name_start,
     artist_start, album_start) = measure_fields(main.getmaxyx()[1])

    if 'songs' in content and content['songs']:  # Write songs header.
        main.addstr(y, 0, '#', crs.color_pair(2)
                    if colour else crs.A_UNDERLINE)
        main.addstr(y, name_start, trunc('Title', name_chars),
                    crs.color_pair(2) if colour else crs.A_UNDERLINE)
        main.addstr(y, artist_start, trunc('Artist', artist_chars),
                    crs.color_pair(2) if colour else crs.A_UNDERLINE)
        main.addstr(y, album_start, trunc('Album', album_chars),
                    crs.color_pair(2) if colour else crs.A_UNDERLINE)
        y += 1

        for song in content['songs']:  # Write each song.
            main.addstr(y, 0, str(i).zfill(2),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            main.addstr(y, name_start, trunc(song['name'], name_chars),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            main.addstr(y, artist_start, trunc(song['artist'], artist_chars),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            main.addstr(y, album_start, trunc(song['album'], album_chars),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            y += 1
            i += 1

    if 'artists' in content and content['artists']:  # Write artists header.
        main.addstr(y, 0, '#', crs.color_pair(2)
                    if colour else crs.A_UNDERLINE)
        main.addstr(y, name_start, trunc('Artist', name_chars),
                    crs.color_pair(2) if colour else crs.A_UNDERLINE)
        y += 1

        for artist in content['artists']:  # Write each artist.
            main.addstr(y, 0, str(i).zfill(2),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            main.addstr(y, name_start, trunc(artist['name'], name_chars),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            y += 1
            i += 1

    if 'albums' in content and content['albums']:  # Write albums header.
        main.addstr(y, 0, '#', crs.color_pair(2)
                    if colour else crs.A_UNDERLINE)
        main.addstr(y, name_start, trunc('Album', name_chars),
                    crs.color_pair(2) if colour else crs.A_UNDERLINE)
        main.addstr(y, artist_start, trunc('Artist', artist_chars),
                    crs.color_pair(2) if colour else crs.A_UNDERLINE)
        y += 1

        for album in content['albums']:  # Write each album.
            main.addstr(y, 0, str(i).zfill(2),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            main.addstr(y, name_start, trunc(album['name'], name_chars),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            main.addstr(y, artist_start, trunc(album['artist'], artist_chars),
                        crs.color_pair(3 if y % 2 == 0 else 4)
                        if colour else 0)
            y += 1
            i += 1

    main.refresh()


def enqueue(arg=None):
    """
    Display the current queue, or add an item to the queue.

    Keyword arguments:
    arg=None: Index of the MusicObject in the main window to add to
      the queue, 'c' to clear the queue, None to display the queue, or
      a space-delimited list of indices to add to the queue, i.e. '1 2 3'.

    Returns: True if an element was successfully inserted. To be used
      when inserting multiple elements.
    """
    global content

    if arg is None:
        if not queue:  # Nothing to display.
            error_msg(outbar, 'The queue is empty.')

        else:  # Display the queue.
            content = queue.collect()

    elif content is None:  # Nothing to queue.
        error_msg(outbar, 'Wrong context for queue.')

    else:
        if arg is 'c':  # Clear the queue.
            addstr(outbar, 'Cleared queue.')
            queue.clear()

        else:
            try:
                num = int(arg)

            except ValueError:
                # Check for multi-option argument.
                try:
                    nums = [int(i) for i in arg.split()]
                except ValueError:
                    error_msg(outbar, 'Invalid argument to queue.')
                else:  # Add all arguments to the queue.
                    count = 0
                    for num in nums:
                        count = count + 1 if enqueue(num) else count
                    addstr(outbar, 'Added %d item%s to the queue.' %
                           (count, '' if count == 1 else 's'))

            else:
                opt = get_option(num)
                if opt is not None:
                    if opt['kind'] == 'artist':  # Artists can't be queued.
                        error_msg(outbar,
                                  'Can only add songs or albums to the queue.')

                    elif opt['id'] in queue.ids:  # Duplicate entry.
                        error_msg(outbar, '\'%s\' is already in the queue.' %
                                  to_string(opt))

                    else:  # Valid  input.
                        addstr(outbar, 'Adding \'%s\' to the queue...' %
                               to_string(opt))
                        queue.append(opt)
                        addstr(outbar, 'Added \'%s\' to the queue.' %
                               to_string(opt))
                        return True

                else:  # num out of range.
                    error_msg(outbar, 'Invalid number. Valid between 1-%d.' %
                              sum([len(content[k]) for k in content.keys()]))


def expand(num=None):
    """
    Display all of a MusicObject's information: songs, artists, and albums.

    Keyword arguments:
    num=None: Index of the MusicObject in the main window to be expanded.
    """
    global content

    if num is None:  # No argument.
        error_msg(outbar, 'Missing argument to play.')

    elif content is None:  # Nothing to expand.
        error_msg(outbar, 'Wrong context for expand.')

    else:
        try:
            num = int(num)

        except ValueError:  # num needs to be an int.
            error_msg(outbar, 'Invalid argument to play.')

        else:
            limit = int((main.getmaxyx()[0] - 6)/3)
            opt = get_option(num, limit)

            if opt is not None:  # Valid input.
                addstr(outbar, 'Loading \'%s\'...' % to_string(opt))
                content = opt.collect(limit=limit)
                outbar.erase()
                outbar.refresh()

            else:  # num out of range.
                error_msg(outbar, 'Invalid number. Valid between 1-%d.' %
                          sum([len(content[k]) for k in content.keys()]))


def help(arg=0):
    """
    Display basic pmcli commands.

    Keyword arguments:
    arg=0: Irrelevant.
    """
    global content
    # Don't use generic addstr() because we don't want to call trunc() here.
    main.erase()
    main.addstr(
        """
        Commands:
        s/search search-term: Search for search-term
        e/expand 123: Expand item number 123
        p/play: Play current queue
        p/play s: Shuffle and play current queue
        p/play 123: Play item number 123
        q/queue: Show current queue
        q/queue 123:  Add item number 123 to queue
        q/queue 1 2 3:  Add items 1, 2, 3 to queue
        q/queue c:  Clear the current queue
        w/write file-name: Write current queue to file file-name
        r/restore file-name: Replace current queue with playlist from file-name
        h/help: Show this help message
        Ctrl-C: Exit pmcli
        """
    )
    main.refresh()
    content = None


def play(arg=None):
    """
    Play a MusicObject or the current queue.

    Keyword arguments:
    arg=None: A number n to play item n, 's' to play the queue in shuffle mode,
      or None to play the current queue in order.
    """
    global content

    if arg is None or arg is 's':
        if not queue:  # Can't play an empty queue.
            error_msg(outbar, 'The queue is empty.')

        else:  # Play the queue.
            if arg is 's':  # Shuffle.
                queue.shuffle()
            content = queue.collect()
            display()
            addstr(outbar, '[spc] pause [q] stop [n] next [9-0] volume')
            queue.play(infobar)
            outbar.erase()  # Remove trailing output.
            outbar.refresh()

    elif content is None:  # Nothing to play.
        error_msg(outbar, 'Wrong context for play.')

    else:
        try:
            num = int(arg)

        except ValueError:  # arg needs to be an int if it isn't 's'.
            error_msg(outbar, 'Invalid argument to play.')

        else:
            opt = get_option(num)

            if opt is not None:  # Valid input.
                addstr(outbar, '[spc] pause [q] stop [n] next [9-0] volume')
                opt.play(infobar)
                addstr(infobar, 'Now playing: None')
                outbar.erase()
                outbar.refresh()

            else:  # num out of range.
                error_msg(outbar, 'Invalid number. Valid between 1-%d' %
                          sum([len(content[k]) for k in content.keys()]))


def restore(fn=None):
    """
    Restore queue from a file.

    Keyword arguments:
    fn=None: Name of the file containing the playlist.
      File should be at ~/.local/share/pmcli/playlists/.
    """
    if fn is None:  # No argument.
        error_msg(outbar, 'Missing argument to restore.')
        return

    path = join(expanduser('~'), '.local', 'share', 'pmcli', 'playlists')
    if not isfile(join(path, fn)):  # Playlist file doesn't exist.
        error_msg(outbar, '%s does not exist.' % fn)
        return

    addstr(outbar, 'Restoring queue from %s...' % fn)
    try:  # Read the playlist.
        json_songs = json.loads(open(join(path, fn)).read())
    except json.decoder.JSONDecodeError:  # Bad file.
        error_msg(outbar, '%s is not a valid playlist file.' % fn)
        return

    songs = []
    for song in json_songs:
        if Song.verify(song):  # Make sure all the data is there.
            songs.append(Song(song, json=True))

    # Replace the current queue with the playlist.
    del queue[:]
    del queue.ids[:]
    queue.extend(songs)
    addstr(outbar, 'Restored %d/%d songs from playlist %s.' %
           (len(songs), len(json_songs), fn))


def search(query=None):
    """
    Search Google Play Music for a given query.

    Keyword arguments:
    query=None: The search query.

    Returns: A dict of lists with keys 'songs', 'artists', and 'albums'.
    """
    global content

    if query is None:  # No argument.
        error_msg(outbar, 'Missing search query.')
        return

    # Fetch as many results as we can display depending on terminal height.
    limit = int((main.getmaxyx()[0] - 3)/3)
    addstr(outbar, 'Searching for \'%s\'...' % query)
    result = api.search(query, max_results=limit)

    outbar.erase()  # Remove trailing output.
    outbar.refresh()

    # 'class' => class of MusicObject
    # 'hits' => key in search result
    # 'key' => per-entry key in search result
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

    # Create 'limit' of each type.
    for i in range(limit):
        for k in content.keys():
            try:
                content[k].append(
                    mapping[k]['class'](next(result[k])[mapping[k]['key']])
                )

            except StopIteration:
                pass

    return content


def write(fn=None):
    """
    Write the current queue to a file.

    Keyword arguments:
    fn=None: File to be written to.
      File is stored at ~/.local/share/pmcli/playlists/.
    """
    if not queue:  # Can't save an empty queue.
        error_msg(outbar, 'Queue is empty.')
        return

    if fn is None:  # No argument.
        error_msg(outbar, 'Missing argument to write.')
        return

    path = join(expanduser('~'), '.local', 'share', 'pmcli', 'playlists')
    if not exists(path):  # No playlists directory.
        error_msg(outbar, 'Path to playlists does not exist.')

    elif exists(join(path, fn)):
        error_msg(outbar, 'Playist %s already exists.' % fn)

    else:  # Write the playlist.
        with open(join(path, fn), 'a') as f:
            json.dump(queue, f)
        addstr(outbar, 'Wrote queue to %s.' % fn)


def addstr(win, string):
    """
    Replace the contents of a window with a new string.
      Not for anything where position matters.

    Arguments:
    win: Window on which to display the string.
    string: String to be displayed.
    """
    win.erase()
    win.addstr(trunc(string, win.getmaxyx()[1]))
    win.refresh()


def error_msg(win, msg):
    """
    Displays an error message.

    Arguments:
    win: Window on which to display the message.
    msg: Message to be displayed.
    """
    addstr(win, 'Error: ' + msg + ' Enter \'h\' or \'help\' for help.')


def hex_to_rgb(hex):
    """
    Convert a hex colour to (r, g, b).
23
    Arguments:
    hex: hexidecimal colour code.

    Returns: (r, g, b) tuple with values 0-1000.
    """
    scalar = 3.9215  # 255 * 3.9215 ~= 1000.
    r = int(int(hex[1:3], 16) * scalar)
    g = int(int(hex[3:5], 16) * scalar)
    b = int(int(hex[5:7], 16) * scalar)

    return r, g, b


def initialize():
    """
    Initialize the windows, read the config, login, and set colours.

    Returns: Whether or not colours are enabled, and curses windows.
    """
    main = crs.initscr()  # Forthe bulk of output.
    main.resize(crs.LINES-3, crs.COLS)
    inbar = crs.newwin(1, crs.COLS, crs.LINES-1, 0)  # For user input.
    infobar = crs.newwin(1, crs.COLS, crs.LINES-2, 0)  # For 'now playing'.
    outbar = crs.newwin(1, crs.COLS, crs.LINES-3, 0)  # For hints and notices.
    crs.curs_set(0)  # Hide the cursor.
    main.addstr(5, int(crs.COLS/2) - 9, 'Welcome to pmcli!')
    main.refresh()

    config = read_config(outbar)

    # Set colours.
    if 'colour' in config:
        crs.start_color()
        init_colours(outbar, config['colour'])
        main.bkgdset(' ', crs.color_pair(1))
        inbar.bkgdset(' ', crs.color_pair(1))
        infobar.bkgdset(' ', crs.color_pair(2))
        outbar.bkgdset(' ', crs.color_pair(4))

    # Log in to Google Play Music.
    addstr(outbar, 'Logging in...')
    login(outbar, config['user'])

    return 'colour' in config, main, inbar, infobar, outbar


def init_colours(win, colours):
    """Set curses colours."""
    try:
        crs.init_color(0, *hex_to_rgb(colours['background']))
        crs.init_color(1, *hex_to_rgb(colours['foreground']))
        crs.init_color(2, *hex_to_rgb(colours['highlight']))
        crs.init_color(3, *hex_to_rgb(colours['content1']))
        crs.init_color(4, *hex_to_rgb(colours['content2']))

    except KeyError:
        addstr(win, 'Config file is missing one or more colours: Exiting.')
        leave(2)

    crs.init_pair(1, 1, 0)
    crs.init_pair(2, 2, 0)
    crs.init_pair(3, 3, 0)
    crs.init_pair(4, 4, 0)


def leave(s):
    """
    Exit gracefully.

    Arguments:
    s: Quit after s seconds.
    """
    sleep(s)
    crs.curs_set(1)
    crs.endwin()
    quit()


def login(win, user):
    """
    Log in to Google Play Music.

    Arguments:
    win: Window on which to display output.
    """
    try:
        if not api.login(
                user['email'], user['password'], user['deviceid']
        ):  # Login failed;
            addstr(win, 'Login failed: Exiting.')
            leave(2)

    except KeyError:  # Invalid config file.
        addstr(win, 'Config file is missing one or more fields: Exiting.')
        leave(2)

    addstr(win, 'Logged in as %s.' % user['email'])  # Login succeeded.


def measure_fields(width):
    """
    Determine max number of  characters and starting point for category fields.

    Arguments:
    width: Width of the window being divided.

    Returns: A tuple containing character allocations and start positions.
    """
    padding = 1  # Space between fields.
    index_chars = 3  # Characters to allocate for index..
    # Width of each field.
    name_chars = artist_chars = album_chars = int(
        (width - index_chars - 3*padding)/3
    )

    total = sum([index_chars, name_chars, artist_chars,
                 album_chars, 3*padding])

    if total != width:  # Allocate any leftover space to name.
        name_chars += width - total

    # Field starting x positions.
    name_start = 0 + index_chars + padding
    artist_start = name_start + name_chars + padding
    album_start = artist_start + artist_chars + padding

    return (index_chars, name_chars, artist_chars, album_chars,
            name_start, artist_start, album_start)


def password(win, config):
    """
    Prompt the user for their password if it is not supplied
      in their config file.

    Arguments:
    win: Window on which to display the prompt.
    config: Parsed config dict.

    Returns: the config dict, either unchanged or with the entered password.
    """
    if not config['user']['password']:
        crs.noecho()  # Don't show the password as it's entered.
        addstr(win, 'Enter your password: ')

        try:
            config['user']['password'] = win.getstr().decode('utf-8')

        except KeyboardInterrupt:
            addstr(win, 'Exiting.')
            leave(1)

        crs.echo()

    return config


def validate_config(config):
    """Verify that a config file has all necessary data."""
    user_valid = (
        'user' in config and 'email' in config['user'] and
        'password' in config['user'] and 'deviceid' in config['user'])

    colours_valid = (
        'colour' not in config or 'enable' in config['colour'] and
        (config['colour']['enable'] != 'yes' or
         ('background' in config['colour'] and
          'foreground' in config['colour'] and
          'highlight' in config['colour'] and
          'content1' in config['colour'] and
          'content2' in config['colour'])))

    return user_valid and colours_valid


def read_config(win):
    """
    Parses a config file for login information.
      Config file should be located at '~/.config/pmcli/config'
      with a section called [auth] containing email, password, and deviceid.

    Arguments:
    win: Window on which to display output.

    Returns: A dict containing keys 'user' and 'colour''.
    """
    path = join(expanduser('~'), '.config', 'pmcli', 'config.json')

    if not isfile(path):
        addstr(win, 'Config file not found at %s: Exiting.' % basename(path))
        leave(2)

    with open(path) as f:
        try:
            with open(path) as f:
                config = password(win, json.load(f))
        except json.decoder.JSONDecodeError:
            addstr(win, 'Invalid config file, please refer to '
                   'config.example: Exiting.')
            leave(2)

    if not validate_config(config):
        addstr(win, 'Invalid config file, please refer to '
               'config.example: Exiting.')
        leave(2)

    try:
        if config['colour']['enable'] == 'no':
            del config['colour']
    except KeyError:
        pass

    return config


def to_string(item):
    """
    Formats a MusicObject's information into a string.

    Arguments:
    item: MusicObject to be formatted.

    Returns: Formatted string.
    """
    if item['kind'] == 'song':
        return ' - '.join((item['name'], item['artist']))
    if item['kind'] == 'artist':
        return item['name']
    if item['kind'] == 'album':
        return ' - '.join((item['name'], item['artist']))

    return str(item)


def time_from_ms(ms):
    """
    Converts milliseconds into mm:ss formatted string.

    Arguments:
    ms: Number of milliseconds.

    Returns: ms in mm:ss.
    """
    ms = int(ms)
    minutes = str(ms // 60000).zfill(2)
    seconds = str(ms // 1000 % 60).zfill(2)
    return "%s:%s" % (minutes, seconds)


def trunc(string, chars):
    """
    Pads a string with '...' if it is too long to fit in a window.

    Arguments:
    string: String to be truncated.
    chars: Max length for the string.

    Returns: The original string if it is short enough to be displayed,
      otherwise the string truncated and padded with '...'.
    """
    if chars < 0 or len(string) <= chars:
        return string
    else:
        return string[:-((len(string) - chars) + 3)] + '...'



class MusicObject(dict):
    """A dict representing a song, artist, or album."""
    def __init__(self, id, name, kind, full):
        """
        MusicObject contstructor.

        Arguments:
        id: Unique item id as determined by gmusicapi.
        name: Title of song/album or name of artist.
        kind: Type of object: song, artist, or album.
        full: Whether or not the item contains all possible information.
          MusicObjects generated from search() results are not full,
          MusicObjects generated from get_{track|artist|album_info}() are full.
        """
        self['id'] = id
        self['name'] = name
        self['kind'] = kind
        self['full'] = full

    @staticmethod
    def play(win, songs):
        """
        Play some songs.

        Arguments:
        win: Window on which to display song information.
        songs: List of songs to play. Songs are tuples following the
          format (song_string, song_id, song_length).

        Returns: None if all items were played, or the index of the
          first unplayed item to be used in restoring the queue.
        """
        conf_path = '~/.config/pmcli/mpv_input.conf'
        i = 1

        for song in songs:
            url = api.get_stream_url(song[0])
            addstr(win, 'Now playing: %s (%s)' %
                   (song[1], song[2]))

            if call(
                    ['mpv', '--really-quiet', '--input-conf', conf_path, url]
            ) is 11:  # 'q' returns this exit code.
                return i if i < len(songs) else None
            i += 1

        return None


class Artist(MusicObject):
    """A dict representing an artist."""
    def __init__(self, artist, full=False):
        """
        Artist constructor.

        Arguments:
        artist: Dict with artist information from gmusicapi.

        Keyword arguments:
        full=False: Whether or not the artist's song list is populated.
        """
        super().__init__(artist['artistId'], artist['name'], 'artist', full)
        self['id'] = artist['artistId']
        self['name'] = artist['name']

        try:
            self['songs'] = [
                {
                    'name': song['title'],
                    'artist': song['artist'],
                    'album': song['album'],
                    'id': song['storeId'],
                    'time': time_from_ms(song['durationMillis']),
                    'kind': 'song'
                } for song in artist['topTracks']
            ]

        except KeyError:
            self['songs'] = []

        try:
            self['albums'] = [
                {
                    'name': album['name'],
                    'artist': album['artist'],
                    'id': album['albumId'],
                    'kind': 'album'
                } for album in artist['albums']
            ]

        except KeyError:
            self['albums'] = []

    def collect(self, limit=20):
        """
        Collect all of an Artist's information: songs, artist, and albums.

        Keyword arguments:
        limit=20: Upper limit of each element to collect,
          determined by terminal height.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
        aggregate = {
            'songs': [],
            'artists': [self],
            'albums': []
        }

        songs = iter(self['songs'])
        albums = iter(self['albums'])

        # Create 'limit' of each type.
        for i in range(limit):
            try:
                aggregate['songs'].append(
                    Song(api.get_track_info(next(songs)['id']))
                )

            except StopIteration:
                pass

            try:
                aggregate['albums'].append(
                    Album(api.get_album_info(next(albums)['id']))
                )

            except StopIteration:
                pass

        return aggregate

    def fill(self, limit):
        """
        If an Artist is not full, fill in its song list.

        Arguments:
        limit: The number of songs to generate, determined by terminal height.

        Returns: A new, full, Artist.
        """
        if self['full']:
            return self

        # Create a new Artist with more information from get_artist_info.
        self = Artist(api.get_artist_info(
            self['id'], max_top_tracks=limit), full=True)
        return self

    def play(self, win):
        """
        Play an Artist's song list.

        Arguments:
        win: Window on which to display song information.
        """
        MusicObject.play(
            win, [(song['id'], to_string(song), song['time'])
                  for song in self['songs']]
        )


class Album(MusicObject):
    """A dict representing an album."""
    def __init__(self, album, full=False):
        """
        Album constructor.

        Arguments:
        artist: Dict with album information from gmusicapi.

        Keyword arguments:
        full=False: Whether or not the album's song list is populated.
        """
        super().__init__(album['albumId'], album['name'], 'album', full)
        self['artist'] = album['artist']
        self['artist_ids'] = album['artistId']
        try:
            self['songs'] = [
                {
                    'name': song['title'],
                    'artist': song['artist'],
                    'artist_id': song['artistId'][0],
                    'album': song['album'],
                    'id': song['storeId'],
                    'time': time_from_ms(song['durationMillis']),
                    'kind': 'song'
                } for song in album['tracks']
            ]

        except KeyError:
            self['songs'] = []

    def collect(self, limit=20):
        """
        Collect all of an Album's information: songs, artist, and albums.

        Keyword arguments:
        limit=20: Upper limit of each element to collect,
          determined by terminal height.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
        aggregate = {
            'songs': [],
            'artists': [
                Artist(api.get_artist_info(id)) for id in self['artist_ids']
            ],
            'albums': [self],
        }

        songs = iter(self['songs'])

        # Create 'limit' of each type.
        for i in range(limit):
            try:
                aggregate['songs'].append(
                    Song(api.get_track_info(next(songs)['id']))
                )

            except StopIteration:
                pass

        return aggregate

    def fill(self, limit=0):
        """
        If an Album is not full, fill in its song list.

        Arguments:
        limit: Irrelevant, we always generate all songs.

        Returns: A new, full, Album.
        """
        if self['full']:
            return self

        # Create a new Album with more information from get_album_info.
        self = Album(api.get_album_info(self['id']), full=True)
        return self

    def play(self, win):
        """
        Play an Album's song list.

        Arguments:
        win: Window on which to display song information.
        """
        MusicObject.play(
            win, [(song['id'], to_string(song), song['time'])
                  for song in self['songs']]
        )


class Song(MusicObject):
    """A dict representing a song."""
    def __init__(self, song, full=True, json=False):
        """
        Song constructor.

        Arguments:
        song: Dict with song information from gmusicapi.

        Keyword arguments:
        full=True: A song is always considered full.
        json=False: Whether or not the song is being initialized from JSON.
        """
        if not json:
            super().__init__(song['storeId'], song['title'], 'song', full)
            self['artist'] = song['artist']
            self['artist_ids'] = song['artistId']
            self['album'] = song['album']
            self['album_id'] = song['albumId']
            self['time'] = time_from_ms(song['durationMillis'])
        else:
            super().__init__(song['id'], song['name'], 'song', full)
            self['artist'] = song['artist']
            self['artist_ids'] = song['artist_ids']
            self['album'] = song['album']
            self['album_id'] = song['album_id']
            self['time'] = song['time']

    @staticmethod
    def verify(item):
        """
        Make sure a dict contains all necessary song data.

        Arguments:
        item: The dict being checked.

        Returns: Whether or not the item contains all necessary data.
        """
        return ('id' in item and 'name' in item and 'kind' in item and
                'full' in item and 'artist' in item and 'artist_ids' in item
                and 'album' in item and 'album_id' in item and 'time' in item)

    def collect(self, limit=None):
        """
        Collect all of a Song's information: songs, artist, and albums.

        Keyword arguments:
        limit=None: Irrelevant.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
        return {
            'songs': [self],
            'artists': [
                Artist(api.get_artist_info(id)) for id in self['artist_ids']
            ],
            'albums': [Album(api.get_album_info(self['album_id']))]
        }

    def fill(self, limit=0):
        """
        All songs are already 'full'.

        Keyword arguments:
        limit=0: Irrelevant.

        Returns: self.
        """
        return self

    def play(self, win):
        """
        Play a Song.

        Arguments:
        win: Window on which to display song information.
        """
        MusicObject.play(win, [(self['id'], to_string(self), self['time'])])


class Queue(list):
    """A queue of songs to be played."""
    def __init__(self):
        """Queue constructor."""
        super().__init__(self)
        self.ids = []

    def append(self, item):
        """
        Add an element to the queue.

        Arguments:
        item: item to be added. This can be a song or album.
          In the case of albums, each song is appended one by one.
        """
        if item['kind'] == 'album':
            for song in item['songs']:
                super().append(Song(api.get_track_info(song['id'])))
                self.ids.append(song['id'])
            # Todo: deal with properly removing album ids.
            self.ids.append(item['id'])

        else:
            super().append(item.fill())
            self.ids.append(item['id'])

    def extend(self, items):
        """
        Add all elements in some iterable to the queue.

        Arguments:
        items: iterable of songs and/or albums to be added one after another.
        """
        for item in items:
            self.append(item)

    def clear(self):
        """Empty the queue."""
        del self[:]
        del self.ids[:]

    def shuffle(self):
        """Shuffle the queue."""
        del self.ids[:]
        songs = [self.pop(0) for i in range(len(self))]
        del self[:]
        shuffle(songs)
        self.extend(songs)

    def collect(self, s=False):
        """
        Collect all of a Queue's information: songs, artist, and albums.

        Keyword arguments:
        s=False: Whether or not the queue is shuffled..

        Returns: A dict with key 'songs'.
        """
        songs = {'songs': [item for item in self]} if len(self) > 0 else None
        if s and songs is not None:
            shuffle(songs['songs'])
        return songs

    def play(self, win):
        """
        Play the queue.

        Arguments:
        win: Window on which to display song information.
        """
        songs = [(song['id'], to_string(song), song['time']) for song in self]

        # Save the queue contents to restore unplayed items.
        cache = []
        for i in range(len(songs)):
            cache.append(self.pop(0))
        del self.ids[:]

        index = MusicObject.play(win, songs)
        addstr(win, 'Now playing: None')

        for item in cache[index:]:
            self.append(item)
            self.ids.append(item['id'])








if __name__ == '__main__':
    colour, main, inbar, infobar, outbar = initialize()
    addstr(infobar, 'Enter \'h\' or \'help\' if you need help.')
    queue = Queue()
    global content
    content = None

    while True:
        transition(get_input())

