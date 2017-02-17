from curses import endwin
from time import sleep


def addstr(win, str):
    # Replace the contents of a window with a new string.
    # Not for anything where position matters.
    win.erase()
    win.addstr(trunc(str, win.getmaxyx()[1]))
    win.refresh()


def to_string(item):
    if item['kind'] == 'song':
        return ' - '.join((item['name'], item['artist']))
    if item['kind'] == 'artist':
        return item['name']
    if item['kind'] == 'album':
        return ' - '.join((item['name'], item['artist']))
    raise ValueError('Invalid type to convert to string.')


def leave(s):
    sleep(s)
    endwin()
    quit()


def measure_fields(width):
    padding = 1
    index_chars = 3
    name_chars = artist_chars = album_chars = int((width - index_chars -
                                                   3*padding)/3)

    total = sum([index_chars, name_chars, artist_chars,
                 album_chars, 3*padding])
    if total != width:
        name_chars += width - total

    name_start = 0 + index_chars + padding
    artist_start = name_start + name_chars + padding
    album_start = artist_start + artist_chars + padding

    return (index_chars, name_chars, artist_chars, album_chars,
            name_start, artist_start, album_start)


def trunc(string, chars):
    if chars < 0 or len(string) <= chars:
        return string
    else:
        return string[:-((len(string) - chars) + 3)] + '...'


def time_from_ms(ms):
    minutes = str(ms // 60000).zfill(2)
    seconds = str(ms // 1000 % 60).zfill(2)
    return "%s:%s" % (minutes, seconds)


def error_msg(bar, msg):
    addstr(bar, 'Error: ' + msg + ' Enter \'h\' or \'help\' for help.')
