#!/usr/bin/env python3

import curses as crs
import json
from gmusicapi import Mobileclient
from os.path import exists, expanduser, join, isfile, basename
from random import shuffle
from getpass import getpass
from subprocess import call
from time import sleep

from warnings import filterwarnings

filterwarnings('ignore')


# -------------------- MUSIC OBJECT CLASSES START -------------------- #

class MusicObject(dict):
    """A dict representing a song, artist, or album."""
    def __init__(self, id, name, kind, full):
        """
        Assign to fields common to Songs, Artists, and Albums.

        Arguments:
        id: Unique item id as determined by gmusicapi.
        name: Title of song/album or name of artist.
        kind: Type of object: song, artist, or album.
        full: Whether or not the item contains all possible information.
          All Songs are full, but in general only Artists and Albums
          generated from get_{artist|album}_info}() are full.
        """
        self['id'] = id
        self['name'] = name
        self['kind'] = kind
        self['full'] = full

    @staticmethod
    def play(songs):
        """
        Play some songs.

        Arguments:
        songs: List of songs to play.

        Returns: None if all songs were played, or the index of the
          first unplayed song to be used in restoring the queue.
        """
        conf_path = join(expanduser('~'), '.config', 'pmcli', 'mpv_input.conf')
        if not isfile(conf_path):
            out.goodbye('No mpv_input.conf found.')
        i = 1

        for song in songs:
            url = api.get_stream_url(song['id'])
            out.now_playing(str(song), song['time'])

            if call(
                    ['mpv', '--really-quiet', '--input-conf', conf_path, url]
            ) == 11:  # 'q' returns this exit code.
                return i if i < len(songs) else None
            i += 1

        return None


class Artist(MusicObject):
    """A dict representing an artist."""
    def __init__(self, artist, full=False):
        """
        # Create a new Artist.

        Arguments:
        artist: Dict with artist information from gmusicapi.

        Keyword arguments:
        full=False: Whether or not the artist's song list is populated.
        """
        super().__init__(artist['artistId'], artist['name'], 'artist', full)
        try:
            self['songs'] = [Song(s) for s in artist['topTracks']]
        except KeyError:
            self['songs'] = []
        try:
            self['albums'] = [Album(a) for a in artist['albums']]
        except KeyError:
            self['albums'] = []

    def __str__(self):
        """
        Format an artist into a string.

        Returns: The artist name.
        """
        return self['name']

    def play(self):
        """Play an artist's song list."""
        MusicObject.play(self['songs'])

    def collect(self, limit=20):
        """
        Collect all of an artist's information: songs, artist, and albums.

        Keyword arguments:
        limit=20: Upper limit of each element to collect,
          determined by terminal height.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
        return {
            'songs': self['songs'][:min(len(self['songs']), limit)],
            'artists': [self],
            'albums': self['albums'][:min(len(self['albums']), limit)]
        }

    def fill(self, limit):
        """
        If an artist is not full, fill in its song list.

        Arguments:
        limit: The number of songs to generate, determined by terminal height.

        Returns: A new, full, Artist.
        """
        if self['full']:
            return self

        self = Artist(api.get_artist_info(
            self['id'], max_top_tracks=limit), full=True)
        return self


class Album(MusicObject):
    """A dict representing an album."""
    def __init__(self, album, full=False):
        """
        Create a new Album

        Arguments:
        artist: Dict with album information from gmusicapi.

        Keyword arguments:
        full=False: Whether or not the album's song list is populated.
        """
        super().__init__(album['albumId'], album['name'], 'album', full)
        self['artist'] = Artist({
            'artistId': album['artistId'][0], 'name': album['artist']})
        try:
            self['songs'] = [Song(s) for s in album['tracks']]
        except KeyError:
            self['songs'] = []

    def __str__(self):
        """Format an album into a string.

        Returns: The album name and artist.
        """
        return ' - '.join((self['name'], self['artist']['name']))

    def play(self):
        """Play an album's song list."""
        MusicObject.play(self['songs'])

    def collect(self, limit=20):
        """
        Collect all of an album's information: songs, artist, and albums.

        Keyword arguments:
        limit=20: Upper limit of each element to collect,
          determined by terminal height.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
        return {
            'songs': self['songs'][:min(len(self['songs']), limit)],
            'artists': [self['artist']],
            'albums': [self]
        }

    def fill(self, limit=0):
        """
        If an album is not full, fill in its song list.

        Arguments:
        limit: Irrelevant, we always generate all songs.

        Returns: A new, full, Album.
        """
        if self['full']:
            return self

        self = Album(api.get_album_info(self['id']), full=True)
        return self


class Song(MusicObject):
    """A dict representing a song."""
    def __init__(self, song, full=True, source='api'):
        """
        Create a new Song.

        Arguments:
        song: Dict with a song's information.

        Keyword arguments:
        full=True: A song is always considered full.
        source='api': The source of the argument dict, which changes how
          we initialize the song.
        """
        if source == 'api':  # Initializing from api results.
            super().__init__(song['storeId'], song['title'], 'song', full)
            self['artist'] = Artist({
                'name': song['artist'], 'artistId': song['artistId'][0]
            })
            self['album'] = Album({
                'name': song['album'], 'albumId': song['albumId'],
                'artist': song['artist'], 'artistId': song['artistId'],
            })
            self['time'] = Song.time_from_ms(song['durationMillis'])
        elif source == 'json':  # Initializing from JSON.
            super().__init__(song['id'], song['name'], 'song', full)
            self['artist'] = song['artist']
            self['album'] = song['album']
            self['time'] = song['time']

    @staticmethod
    def verify(item):
        """
        Make sure a dict contains all necessary song data.

        Arguments:
        item: The dict being checked.

        Returns: Whether or not the item contains sufficient data.
        """
        return ('id' in item and 'name' in item and 'kind' in item and
                'full' in item and 'artist' in item and 'album' in item
                and 'time' in item)

    @staticmethod
    def time_from_ms(ms):
        """
        Converts milliseconds into a mm:ss formatted string.

        Arguments:
        ms: Number of milliseconds.

        Returns: ms in mm:ss.
        """
        ms = int(ms)
        minutes = str(ms // 60000).zfill(2)
        seconds = str(ms // 1000 % 60).zfill(2)
        return "%s:%s" % (minutes, seconds)

    def __str__(self):
        """
        Format a song into a string.

        Returns: The song title, artist name, and album name.
        """
        return ' - '.join((self['name'], self['artist']['name']))

    def play(self):
        """Play a song."""
        MusicObject.play([self])

    def collect(self, limit=None):
        """
        Collect all of a song's information: songs, artist, and albums.

        Keyword arguments:
        limit=None: Irrelevant.

        Returns: A dict of lists with keys 'songs, 'artists', and 'albums'.
        """
        return {
            'songs': [self],
            'artists': [self['artist']],
            'albums': [self['album']]
        }

    def fill(self, limit=0):
        """
        Do nothing. All songs are already 'full'.

        Keyword arguments:
        limit=0: Irrelevant.

        Returns: self.
        """
        return self


class Queue(list):
    """A queue of songs to be played."""
    def __init__(self):
        """Create an empty Queue."""
        super().__init__(self)

    def append(self, item):
        """
        Add an element to the queue.

        Arguments:
        item: item to be added. This can be a song or album.
          In the case of albums, each song is appended one by one.

        Returns: Number of songs that were added.
        """
        if item['kind'] == 'album':
            super().extend(item['songs'])
            return len(item['songs'])
        elif item['kind'] == 'song':
            super().append(item)
            return 1
        else:
            raise TypeError('Adding invalid type to queue.')

    def extend(self, items):
        """
        Add all elements in some iterable to the queue. Extend follows
          the same rules as append.

        Arguments:
        items: iterable of items to be added one after another.

        Returns: number of songs that were successfully inserted.
        """
        return sum([self.append(item) for item in items])

    def collect(self, limit=-1):
        """
        Collect all of a Queue's information: songs, artist, and albums.

        Keyword arguments:
        limit=-1: Max number of queue items to display, determined by
          terminal height.

        Returns: A dict with key 'songs'.
        """
        return {'songs':
                self[:min(limit, len(self)) if limit != -1 else len(self)]}

    def play(self):
        """Play the queue. If playback is halted, restore unplayed items."""
        cache = self[:]
        del self[:]
        index = MusicObject.play(cache)
        out.now_playing()
        self.extend(cache[index:])


class Content():
    """
    A Content object holds all of the information to be displayed
    on the main window.
    """
    def __init__(self):
        """Create an empty Content."""
        self.content = {'songs': [], 'artists': [], 'albums': []}


# -------------------- MUSIC OBJECT CLASSES END -------------------- #

# -------------------------- WRITER START -------------------------- #


class Writer():

    def __init__(
            self, main, inbar, infobar, outbar,
            curses=True, colour=False, test=False):
        """
        Writer constructor.

        Arguments:
        main/inbar/infobar/outbar: curses windows.

        Keyword arguments:
        curses=True: Flag for disabling curses output.
        colour=False: Flag for disabling colour output.
        test=False: Flag to disable all output for unit testing.
          If test is True, then curses must be disabled.
        """
        if test and curses:
            print('Incompatible arguments to writer: '
                  'curses must be disabled to test.')
            sleep(1)
            quit()
        self.main = main
        self.inbar = inbar
        self.infobar = infobar
        self.outbar = outbar
        self.curses = curses
        self.colour = colour
        self.test = test

    @staticmethod
    def trunc(string, ch):
        """
        Pads a string with '...' if it is too long to fit in a window.

        Arguments:
        string: String to be truncated.
        ch: Max length for the string.

        Returns: The original string if it is short enough to be displayed,
          otherwise the string truncated and padded with '...'.
        """
        if ch < 0 or len(string) <= ch:
            return string
        else:
            return string[:-((len(string) - ch) + 3)] + '...'

    def addstr(self, win, string):
        """
        Replace the contents of a window with a new string.
          Not for anything where position matters.

        Arguments:
        win: Window on which to display the string.
        string: String to be displayed.
        """
        if not self.curses:
            if not self.test:
                print(string)
            return

        win.erase()
        win.addstr(Writer.trunc(string, win.getmaxyx()[1]))
        win.refresh()

    def refresh(self):
        """Refresh all windows."""
        if not self.curses:
            return

        self.main.refresh()
        self.inbar.refresh()
        self.infobar.refresh()
        self.outbar.refresh()

    def now_playing(self, string=None, time=None):
        """
        Show 'now playing' information. If both kwargs are None,
          nothing is playing.

        Keyword arguments:
        string=None: Formatted song string.
        time=None: Length of the song playing.
        """
        if self.test:
            return

        if string is None or time is None:
            self.addstr(self.infobar, 'Now playing: None')
        else:
            self.addstr(self.infobar, 'Now playing: %s (%s)' % (string, time))

    def erase_outbar(self):
        """Erases content on the outbar."""
        if not self.curses:
            return

        self.outbar.erase()
        self.outbar.refresh()

    def error_msg(self, msg):
        """
        Displays an error message.

        Arguments:
        win: Window on which to display the message.
        msg: Message to be displayed.
        """
        if self.test:
            return

        self.addstr(
            self.outbar, 'Error: %s. Enter \'h\' or \'help\' for help.' % msg)

    def welcome(self):
        """Displays a welcome message."""
        if not self.curses:
            if not self.test:
                print('Welcome to pmcli!')
            return

        self.main.addstr(5, int(crs.COLS/2) - 9, 'Welcome to pmcli!')
        self.main.refresh()

    def goodbye(self, msg):
        """
        Exit pmcli.

        Arguements:
        msg: Message to display prior to exiting.
        """
        if not self.curses:
            if not self.test:
                print('Goodbye.')
            quit()

        self.addstr(self.outbar, msg)
        sleep(2)
        crs.curs_set(1)
        crs.endwin()
        quit()

    def get_input(self):
        """
        Get user input in the bottom bar.

        Returns: The user-inputted string.
        """
        if not self.curses:
            return input('Enter some input: ')

        self.addstr(self.inbar, '> ')
        crs.curs_set(2)  # Show the cursor.

        try:
            string = self.inbar.getstr()
        except KeyboardInterrupt:
            self.goodbye('Goodbye, thanks for using pmcli!')

        self.inbar.deleteln()
        crs.curs_set(0)  # Hide the cursor.

        return string.decode('utf-8')

    def outbar_msg(self, msg):
        """
        Display a basic output message.

        Arguments:
        msg: Message to be displayed.
        """
        if self.test:
            return
        self.addstr(self.outbar, msg)

    def display(self):
        """Update the main window with some content."""
        if not self.curses:
            if not self.test:
                if 'songs' in c.content and c.content['songs']:
                    print('Songs:')
                for song in c.content['songs']:
                    print(str(song))
                if 'artists' in c.content and c.content['artists']:
                    print('Artists:')
                for artist in c.content['artists']:
                    print(str(artist))
                if 'albums' in c.content and c.content['albums']:
                    print('Albums:')
                for album in c.content['albums']:
                    print(str(album))
            return

        def measure_fields(width):
            """
            Determine max number of  characters and starting point
              for category fields.

            Arguments:
            width: Width of the window being divided.

            Returns: A tuple containing character allocations
              and start positions.
            """
            padding = 1  # Space between fields.
            i_ch = 3  # Characters to allocate for index.
            # Width of each name, artist, and album fields.
            n_ch = ar_ch = al_ch = int((width - i_ch - 3*padding)/3)

            total = sum([i_ch, n_ch, ar_ch, al_ch, 3*padding])

            if total != width:  # Allocate any leftover space to name.
                n_ch += width - total

            # Field starting x positions.
            n_start = 0 + i_ch + padding
            ar_start = n_start + n_ch + padding
            al_start = ar_start + ar_ch + padding

            return (i_ch, n_ch, ar_ch, al_ch,
                    n_start, ar_start, al_start)

        cl = self.colour
        self.main.erase()
        y, i = 0, 1  # y coordinate in main window, current item index.
        (i_ch, n_ch, ar_ch, al_ch, n_start,
         ar_start, al_start) = measure_fields(out.main.getmaxyx()[1])

        if 'songs' in c.content and c.content['songs']:  # Songs header.
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, n_start, Writer.trunc('Title', n_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, ar_start, Writer.trunc('Artist', ar_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, al_start, Writer.trunc('Album', al_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)

            y += 1

            for song in c.content['songs']:  # Write each song.
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, n_start, Writer.trunc(song['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, ar_start, Writer.trunc(song['artist']['name'], ar_ch),  # noqa
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, al_start, Writer.trunc(song['album']['name'], al_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)

                y += 1
                i += 1

        if 'artists' in c.content and c.content['artists']:  # Artists header.
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, n_start, Writer.trunc('Artist', n_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)

            y += 1

            for artist in c.content['artists']:  # Write each artist.
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, n_start, Writer.trunc(artist['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)

                y += 1
                i += 1

        if 'albums' in c.content and c.content['albums']:  # Albums header.
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, n_start, Writer.trunc('Album', n_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, ar_start, Writer.trunc('Artist', ar_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)

            y += 1

            for album in c.content['albums']:  # Write each album.
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, n_start, Writer.trunc(album['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, ar_start, Writer.trunc(album['artist']['name'], ar_ch),  # noqa
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)

                y += 1
                i += 1

        self.main.refresh()


# --------------------------- WRITER END --------------------------- #

# ------------------- LACK OF ORGANIZATION START ------------------- #


def transition(input):
    """
    Route input to the appropriate function.

    Arguments:
    input: User input.
    """
    commands = {  # Command -> function mapping.
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
    if c.content is None:
        out.now_playing()

    try:
        command, arg = input.split(maxsplit=1)
    except ValueError:  # No argument.
        command = input

    if command in commands:
        commands[command](arg)
        if c.content is not None and out.curses:
            out.display()
    else:
        out.error_msg('Nonexistent command')


def get_option(num, limit=-1):
    """
    Select a numbered MusicObject from the main window.

    Arguments:
    num: Index of the MusicObject in the main window to be returned.

    Keyword argumnents:
    limit=-1: Number of songs to generate for artists,
      determined by terminal height.

    Returns: The MusicObject at index 'num'.
    """
    total = sum([len(c.content[k]) for k in c.content.keys()])
    if num < 0 or num > total:
        out.error_msg('Index out of range: valid between 1-%d' % total)
        return None

    i = 1
    for key in ('songs', 'artists', 'albums'):  # Hardcoded to guarantee order.
        for item in c.content[key]:
            if i == num:
                return item.fill(limit)  # Always return item with all content.
            else:
                i += 1


def enqueue(arg=None):
    """
    Display the current queue, or add an item to the queue.

    Keyword arguments:
    arg=None: Index of the MusicObject in the main window to add to
      the queue, 'c' to clear the queue, None to display the queue, or
      a space-delimited list of indices to add to the queue, i.e. '1 2 3'.
    """
    if arg is None:
        if not queue:  # Nothing to display.
            out.error_msg('The queue is empty')

        else:  # Display the queue.
            if out.curses:
                limit = out.main.getmaxyx()[0] - 1  # Allow room for header.
            else:
                limit = -1
            if queue:
                c.content = queue.collect(limit)
            else:
                out.error_msg('Wrong context for queue')

    else:
        if arg is 'c':  # Clear the queue.
            out.outbar_msg('Cleared queue.')
            del queue[:]

        else:
            try:
                num = int(arg)

            except ValueError:
                try:  # Check for multi-option argument.
                    nums = [int(i) for i in arg.split()]
                except ValueError:  # Invalid argument.
                    out.error_msg('Invalid argument to queue')
                else:  # Add all arguments to the queue.
                    out.outbar_msg('Adding items to the queue...')
                    items = [get_option(num) for num in nums]
                    count = queue.extend(
                        [item for item in items if item is not None])
                    out.outbar_msg('Added %d song%s to the queue.' %
                                   (count, '' if count == 1 else 's'))

            else:
                if (num > len(c.content['songs']) and
                    num <= len(c.content['songs']) + len(c.content['artists'])):  # noqa
                    out.error_msg('Can only add songs or albums to the queue.')
                else:
                    item = get_option(num)
                    if item is not None:
                        count = queue.append(item)
                        # I feel so dirty using double quotes.
                        out.outbar_msg("Added %d song%s to the queue." %
                                       (count, '' if count == 1 else 's'))


def expand(num=None):
    """
    Display all of a MusicObject's information: songs, artists, and albums.

    Keyword arguments:
    num=None: Index of the MusicObject in the main window to be expanded.
    """
    if num is None:  # No argument.
        out.error_msg('Missing argument to play')
    elif c.content is None:  # Nothing to expand.
        out.error_msg('Wrong context for expand.')
    else:
        try:
            num = int(num)
        except ValueError:  # num needs to be an int.
            out.error_msg('Invalid argument to play')
        else:
            if not out.curses:
                limit = -1
            else:
                # Artists only have one artist and albums only have one album,
                # so we can allocate more space for the other fields.
                limit = int((out.main.getmaxyx()[0] - 9)/2)
            item = get_option(num, limit)

            if item is not None:  # Valid input.
                c.content = item.collect(limit=limit)
                out.erase_outbar()


def help(arg=0):
    """
    Display basic pmcli commands.

    Keyword arguments:
    arg=0: Irrelevant.
    """
    c.content = None
    if not out.curses:
        return

    # Don't use generic addstr() because we don't want to call trunc() here.
    out.main.erase()
    out.main.addstr(
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
    out.main.refresh()


def play(arg=None):
    """
    Play a MusicObject or the current queue.

    Keyword arguments:
    arg=None: A number n to play item n, 's' to play the queue in shuffle mode,
      or None to play the current queue in order.
    """
    if arg is None or arg is 's':
        if not queue:  # Can't play an empty queue.
            out.error_msg('The queue is empty')
        else:  # Play the queue.
            if arg is 's':  # Shuffle.
                shuffle(queue)
            if out.curses:
                limit = out.main.getmaxyx()[0] - 1  # Allow room for header.
            else:
                limit = -1
            c.content = queue.collect(limit)
            out.display()
            out.outbar_msg(
                '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
            queue.play()
            out.erase_outbar()

    elif c.content is None:  # Nothing to play.
        out.error_msg('Wrong context for play')
    else:
        try:
            num = int(arg)
        except ValueError:  # arg needs to be an int if it isn't 's'.
            out.error_msg('Invalid argument to play')
        else:
            item = get_option(num)

            if item is not None:  # Valid input.
                out.outbar_msg(
                    '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
                item.play()
                out.now_playing()
                out.erase_outbar()


def restore(fn=None):
    """
    Restore queue from a file.

    Keyword arguments:
    fn=None: Name of the file containing the playlist.
      File should be at ~/.local/share/pmcli/playlists/.
    """
    path = join(expanduser('~'), '.local', 'share', 'pmcli', 'playlists')
    if fn is None:  # No argument.
        out.error_msg('Missing argument to restore')
    elif not isfile(join(path, fn)):  # Playlist file doesn't exist.
        out.error_msg('Playlist %s does not exist' % fn)
    else:
        out.outbar_msg('Restoring queue from %s...' % fn)
        try:  # Read the playlist.
            with open(join(path, fn)) as f:
                json_songs = json.load(f)
        except json.decoder.JSONDecodeError:  # Bad file.
            out.error_msg('%s is not a valid playlist file' % fn)
        else:
            songs = [Song(song, source='json')
                     for song in json_songs if Song.verify(song)]

            # Replace the current queue with the playlist.
            del queue[:]
            queue.extend(songs)
            out.outbar_msg('Restored %d songs from playlist %s.' %
                           (len(songs), fn))


def search(query=None):
    """
    Search Google Play Music for a given query.

    Keyword arguments:
    query=None: The search query.

    Returns: A dict of lists with keys 'songs', 'artists', and 'albums'.
    """
    if query is None:  # No argument.
        out.error_msg('Missing search query')
        return

    # Fetch as many results as we can display depending on terminal height.
    if out.curses:
        limit = int((out.main.getmaxyx()[0] - 3)/3)
    else:
        limit = 50

    out.outbar_msg('Searching for \'%s\'...' % query)
    result = api.search(query, max_results=limit)
    out.erase_outbar()

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
    c.content = {'songs': [], 'artists': [], 'albums': []}
    iters = {k: iter(result[mapping[k]['hits']]) for k in c.content.keys()}

    # Create at most 'limit' of each type.
    for i in range(limit):
        for k in iters.keys():
            try:
                c.content[k].append(
                    mapping[k]['class'](next(iters[k])[mapping[k]['key']]))
            except StopIteration:
                pass


def write(fn=None):
    """
    Write the current queue to a file.

    Keyword arguments:
    fn=None: File to be written to.
      File is stored at ~/.local/share/pmcli/playlists/.
    """
    path = join(expanduser('~'), '.local', 'share', 'pmcli', 'playlists')
    if not queue:  # Can't save an empty queue.
        out.error_msg('Queue is empty')
    elif fn is None:  # No argument.
        out.error_msg('Missing argument to write')
    elif not exists(path):  # No playlists directory.
        out.error_msg('Path to playlists does not exist')
    elif exists(join(path, fn)):  # Playlist already exists at path/fn.
        out.error_msg('Playist %s already exists' % fn)
    else:  # Write the playlist.
        with open(join(path, fn), 'a') as f:
            json.dump(queue, f)
        out.outbar_msg('Wrote queue to %s.' % fn)


# ------------------------- LOGIN STUFF START ------------------------- #


def validate_config(config):
    """
    Verify that a config file has all necessary data.
      If the check fails, the program ends.

    Arguments:
    config: Config to be checked.

    Returns: Whether or not the config file has colour support.
    """

    def validate_colour(hex):
        """
        Verify that a string represents a valid hex colour.

        Arguments:
        hex: String to be checked.

        Returns: Whether or not the string is a hex colour.
        """
        # ASCII values for letters and numbers.
        c = tuple(range(48, 58)) + tuple(range(65, 91)) + tuple(range(97, 123))

        return (hex.startswith('#') and len(hex) == 7 and
                all([ord(ch) in c for ch in hex[1:]]))

    user_fields = ['email', 'password', 'deviceid']
    colour_fields = ['background', 'foreground',
                     'highlight', 'content1', 'content2']

    # Check if there is any user info.
    if 'user' not in config:
        out.goodbye('No user info in config file: Exiting.')

    # Check if there is enough user info.
    if not all([k in config['user'] for k in user_fields]):
        out.goodbye('Missing user info in config file: Exiting.')

    # Check if there is any colour info.
    if 'colour' in config and 'enable' not in config['colour']:
        out.goodbye('Missing colour enable flag in config file: Exiting.')
    else:
        colour = config['colour']['enable'] == 'yes'

    # Check if the colours are valid.
    if colour and not all([c in config['colour'] for c in colour_fields]):
        out.outbar_msg('One or more colours are missing: Not using colour.')
        colour = False
        sleep(1.5)
    elif colour and not all([validate_colour(config['colour'][c])
                             for c in colour_fields]):
        out.outbar_msg('One or more colours are invalid: Not using colour.')
        colour = False
        sleep(1.5)

    return colour


def password(config):
    """
    Prompt the user for their password if it is not supplied
      in their config file.

    Arguments:
    config: Dict of config info.

    Returns: the config dict, either unchanged or with
      the entered password.
    """
    if not config['user']['password']:
        if not out.curses:
            try:
                config['user']['password'] = getpass()
            except KeyboardInterrupt:
                out.goodbye('Exiting.')
        else:
            crs.noecho()  # Don't show the password as it's entered.
            out.addstr(out.inbar, 'Enter your password: ')
            try:
                config['user']['password'] = out.inbar.getstr().decode('utf-8')  # noqa
            except KeyboardInterrupt:
                out.gooodbye('Exiting.')
            crs.echo()

    return config


def read_config():
    """
    Parses a config file for login information.
      Config file should be located at '~/.config/pmcli/config'
      with a section called [auth] containing email, password,
      and deviceid.

    Returns: A dict containing keys 'user' and 'colour''.
    """

    path = join(expanduser('~'), '.config', 'pmcli', 'config.json')

    if not isfile(path):
        out.goodbye('Config file not found at %s: Exiting.' % basename(path))

    with open(path) as f:
        try:
            config = json.load(f)
        except json.decoder.JSONDecodeError:
            out.goodbye('Invalid config file, please refer to '
                        'config.example: Exiting.')

    return config


def get_windows():
    """
    Initialize the curses windows.

    Returns: Curses windows.
    """
    main = crs.initscr()  # Forthe bulk of output.
    main.resize(crs.LINES-3, crs.COLS)
    inbar = crs.newwin(1, crs.COLS, crs.LINES-1, 0)  # For user input.
    infobar = crs.newwin(1, crs.COLS, crs.LINES-2, 0)  # For 'now playing'.
    outbar = crs.newwin(1, crs.COLS, crs.LINES-3, 0)  # For notices.
    return main, inbar, infobar, outbar


def set_colours(colours):
    """
    Set curses colours.

    Arguments:
    colours: Dict with colour information.
    """

    def hex_to_rgb(hex):
        """
        Convert a hex colour to (r, g, b).

        Arguments:
        hex: Hexidecimal colour code, i.e. '#abc123'.

        Returns: (r, g, b) tuple with values 0-1000.
        """

        scalar = 3.9215  # 255 * 3.9215 ~= 1000.
        r = int(int(hex[1:3], 16) * scalar)
        g = int(int(hex[3:5], 16) * scalar)
        b = int(int(hex[5:7], 16) * scalar)

        return (r, g, b)

    crs.start_color()
    # Define colours.
    crs.init_color(0, *hex_to_rgb(colours['background']))
    crs.init_color(1, *hex_to_rgb(colours['foreground']))
    crs.init_color(2, *hex_to_rgb(colours['highlight']))
    crs.init_color(3, *hex_to_rgb(colours['content1']))
    crs.init_color(4, *hex_to_rgb(colours['content2']))

    # Define colour pairs.
    crs.init_pair(1, 1, 0)
    crs.init_pair(2, 2, 0)
    crs.init_pair(3, 3, 0)
    crs.init_pair(4, 4, 0)

    # Set colours.
    crs.start_color()
    out.main.bkgdset(' ', crs.color_pair(1))
    out.inbar.bkgdset(' ', crs.color_pair(1))
    out.infobar.bkgdset(' ', crs.color_pair(2))
    out.outbar.bkgdset(' ', crs.color_pair(4))

    out.refresh()


def easy_login():
    """One-step login for debugging."""
    config = (password(read_config()))
    validate_config(config)
    user = config['user']

    if not api.login(user['email'], user['password'], user['deviceid']):
        print('Login failed: exiting.')
        quit()
    else:
        print('Logged in as %s (%s).' %
              (user['email'], 'Full' if api.is_subscribed else 'Free'))


def login(user):
    """
    Log into Google Play Music. Succeeds or exits.

    Arguments:
    user: Dict containing auth information.
    """
    crs.curs_set(0)
    out.outbar_msg('Logging in...')
    if not api.login(user['email'], user['password'], user['deviceid']):
        out.goodbye('Login failed: Exiting.')
    out.outbar_msg('Logging in... Logged in as %s (%s).' %
                   (user['email'], 'Full' if api.is_subscribed else 'Free'))


# --------------------------- LOGIN STUFF END --------------------------- #


api = Mobileclient()
queue = Queue()
out = Writer(None, None, None, None, curses=False)
c = Content()

if __name__ == '__main__':
    out = Writer(*get_windows())
    config = password(read_config())
    colour = validate_config(config)
    if colour:
        set_colours(config['colour'])
        out.colour = True
    out.welcome()
    login(config['user'])
    out.addstr(out.infobar, 'Enter \'h\' or \'help\' if you need help.')

    while True:
        transition(out.get_input())
else:
    easy_login()
