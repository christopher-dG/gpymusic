from curses import endwin
from time import sleep


def addstr(win, str):
    # Replace the contents of a window with a new string.
    # Not for anything where position matters.
    win.erase()
    win.addstr(str)
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
    index_chars = 3
    name_chars = artist_chars = album_chars = int((width - index_chars)/3)

    total = sum([index_chars, name_chars, artist_chars, album_chars])
    if total != width:
        name_chars += width - total

    name_start = 0 + index_chars
    artist_start = name_start + name_chars
    album_start = artist_start + artist_chars
    return (index_chars, name_chars, artist_chars, album_chars,
            name_start, artist_start, album_start)


def trunc(string, chars):
    if chars < 0 or len(string) <= chars:
        return string
    else:
        return string[:-((len(string) - chars) + 3)] + '...'
