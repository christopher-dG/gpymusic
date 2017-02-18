from curses import endwin, curs_set
from time import sleep


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


def leave(s):
    """
    Exit gracefully.

    Arguments:
    s: Quit after s seconds.
    """
    sleep(s)
    curs_set(1)
    endwin()
    quit()


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
    raise ValueError('Invalid type to convert to string.')


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
