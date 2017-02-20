#!/usr/bin/env python3

import curses as crs
from gmusicapi import Mobileclient
from os.path import exists, expanduser, join, isfile, basename
from random import shuffle
from subprocess import call
from time import sleep
import json
import warnings

warnings.filterwarnings('ignore')

api = Mobileclient()  # Our interface to Google Music.


# -------------------- MUSIC OBJECT CLASSES START -------------------- #

class MusicObject(dict):
    """A dict representing a song, artist, or album."""
    def __init__(self, id, name, kind, full):
        """
        MusicObject constructor.

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
        songs: List of songs to play. Songs are tuples following the
          format (song_string, song_id, song_length).

        Returns: None if all items were played, or the index of the
          first unplayed item to be used in restoring the queue.
        """
        conf_path = '~/.config/pmcli/mpv_input.conf'
        i = 1

        for song in songs:
            url = api.get_stream_url(song['id'])
            out.now_playing(song.to_string(), song['time'])

            if (call(['mpv', '--really-quiet', '--input-conf', conf_path, url])
                is 11):  # 'q' returns this exit code.
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
        try:
            self['songs'] = [Song(s) for s in artist['topTracks']]
        except KeyError:
            self['songs'] = []
        try:
            self['albums'] = [Album(a) for a in artist['albums']]
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
        return {
            'songs': self['songs'][:min(len(self['songs']), limit)],
            'artists': [self],
            'albums': self['albums'][:min(len(self['albums']), limit)]
        }

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

    def to_string(self):
        """
        Format an Artist into a string.

        Returns: The artist name.
        """
        return self['name']

    def play(self):
        """Play an Artist's song list."""
        MusicObject.play(self['songs'])


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
        self['artist'] = Artist({
            'artistId': album['artistId'][0], 'name': album['artist']})
        try:
            self['songs'] = [Song(s) for s in album['tracks']]
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
        return {
            'songs': self['songs'][:min(len(self['songs']), limit)],
            'artists': [self['artist']],
            'albums': [self]
        }

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

    def to_string(self):
        """Format an Album into a string.

        Returns: The album name and artist.
        """
        return ' - '.join((item['name'], item['artist']))

    def play(self):
        """Play an Album's song list."""
        MusicObject.play(self['songs'])


class Song(MusicObject):
    """A dict representing a song."""
    def __init__(self, song, full=True, source='api'):
        """
        Song constructor.

        Arguments:
        song: Dict with song information from gmusicapi.

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
        elif source == 'json':  # Initializing from JSON
            super().__init__(song['id'], song['name'], 'song', full)
            self['artist'] = song['artist']
            self['album'] = song['album']
            self['time'] = song['time']
        else:
            raise TypeError('Initializing Song from bad type.')

    @staticmethod
    def verify(item):
        """
        Make sure a dict contains all necessary song data.

        Arguments:
        item: The dict being checked.

        Returns: Whether or not the item contains all necessary data.
        """
        return ('id' in item and 'name' in item and 'kind' in item and
                'full' in item and 'artist' in item and 'album' in item
                and 'time' in item)

    @staticmethod
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

    def collect(self, limit=None):
        """
        Collect all of a Song's information: songs, artist, and albums.

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
        All songs are already 'full'.

        Keyword arguments:
        limit=0: Irrelevant.

        Returns: self.
        """
        return self

    def to_string(self):
        return ' - '.join((self['name'], self['artist']))

    def play(self):
        """Play a Song."""
        MusicObject.play(self)


class Queue(list):
    """
    A queue of songs to be played. Duplicate songs are not
    allowed in the queue.
    """
    def __init__(self):
        """Queue constructor."""
        super().__init__(self)
        self.ids = []

    def append(self, item):
        """
        Add an element to the queue if it is not already in the queue.

        Arguments:
        item: item to be added. This can be a song or album.
          In the case of albums, each song is appended one by one.
          Songs are inserted in order, but certain songs may be
          skipped if they are already in the queue.

        Returns: Number of songs that were successfully added.
        """
        count = 0
        if item['kind'] == 'album':
            for song in item['songs']:
                if song['id'] not in self.ids:
                    super().append(song)
                    self.ids.append(song['id'])
                    count += 1
        else:
            if item['id'] not in self.ids:
                super().append(item)
                self.ids.append(item['id'])
                count += 1

        return count

    def extend(self, items):
        """
        Add all elements in some iterable to the queue. Extend follows
          the same rules as append.

        Arguments:
        items: iterable of items to be added one after another.

        Returns: number of songs that were successfully inserted.
        """
        count = 0
        for song in songs:
            count += self.append(song)

        return count

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
        songs = {'songs': self} if len(self) > 0 else None
        if s and songs is not None:
            shuffle(songs['songs'])

        return songs

    def play(self):
        """Play the queue."""

        # Save the queue contents to restore unplayed items.
        cache = []
        for i in range(len(self)):
            cache.append(self.pop(0))
        del self.ids[:]

        index = MusicObject.play(win, self)
        out.now_playing()
        self.extend(cache[index:])


# -------------------- MUSIC OBJECT CLASSES END -------------------- #

# ------------------------- CRSWRITER START ------------------------- #


class CrsWriter():

    def __init__(
            self, main, inbar, infobar, outbar, disable=False, colour=False):
        """
        CrsWriter constructor.

        Arguments:
        main/inbar/infobar/outbar: curses windows.
        
        Keyword arguments:
        disable=False: Flag for disabling curses output.
        colour=False: Flag for disabling colour output.
        """

        self.main = main
        self.inbar = inbar
        self.infobar = infobar
        self.outbar = outbar
        self.disable = disable

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
        if self.disable:
            return

        win.erase()
        win.addstr(CrsWriter.trunc(string, win.getmaxyx()[1]))
        win.refresh()

    def now_playing(self, string=None, time=None):
        """
        Show 'now playing' information. If both kwargs are None,
          nothing is playing.

        Keyword arguments:
        string=None: Formatted song string.
        time=None: Length of the song playing.
        """
        if self.disable:
            return
        
        if string is None or time is None:
            self.addstr(self.infobar, 'Now playing: None')
        else:
            self.addstr(self.infobar, 'Now playing: %s %s' % (string, time))

    def error_msg(self, msg):
        """
        Displays an error message.

        Arguments:
        win: Window on which to display the message.
        msg: Message to be displayed.
        """
        if self.disable:
            return

        self.addstr(
            outbar, 'Error: ' + msg + ' Enter \'h\' or \'help\' for help.')

    def welcome(self):
        self.main.addstr(5, int(crs.COLS/2) - 9, 'Welcome to pmcli!')
        self.main.refresh()

    def goodbye(self, msg):
        """
        Exit pmcli.

        Arguements:
        msg: Message to display prior to exiting.
        """
        if self.disable:
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
        if disable:
            return input('Enter some input: ')

        self.addstr(self.inbar, '> ')
        crs.curs_set(2)  # Show the cursor.

        try:
            input = inbar.getstr().decode('utf-8')
        except KeyboardInterrupt:
            self.addstr(self.outbar, 'Goodbye, thanks for using pmcli!')
            leave(1)

        inbar.deleteln()
        crs.curs_set(0)  # Hide the cursor.

        return input.decode('utf-8')

    def outbar_msg(self, msg):
        """
        Display a basic output message.

        Arguments:
        msg: Message to be displayed.
        """
        if disable:
            return

        self.addstr(outbar, msg)


    def display(self):
        """Update the main window with some content."""
        if self.disable:
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


        c = self.colour
        self.main.erase()
        y, i = 0, 1  # y coordinate in main window, current item index.
        (i_ch, n_ch, ar_ch, al_ch, n_start,
         ar_start, al_start) = measure_fields(main.getmaxyx()[1])

        if 'songs' in content and content['songs']:  # Songs header.
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if c else crs.A_UNDERLINE)
            self.main.addstr(
                y, n_start, CrsWriter.trunc('Title', n_ch),
                crs.color_pair(2) if c else crs.A_UNDERLINE)
            self.main.addstr(
                y, ar_start, CrsWriter.trunc('Artist', ar_ch),
                crs.color_pair(2) if c else crs.A_UNDERLINE)
            self.main.addstr(
                y, al_start, CrsWriter.trunc('Album', al_ch),
                crs.color_pair(2) if c else crs.A_UNDERLINE)

            y += 1

            for song in content['songs']:  # Write each song.
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)
                self.main.addstr(
                    y, n_start, CrsWriter.trunc(song['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)
                self.main.addstr(
                    y, ar_start, CrsWriter.trunc(song['artist'], ar_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)
                self.main.addstr(
                    y, al_start, CrsWriter.trunc(song['album'], al_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)

                y += 1
                i += 1

        if 'artists' in content and content['artists']:  # Artists header.
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if c else crs.A_UNDERLINE)
            self.main.addstr(
                y, n_start, CrsWriter.trunc('Artist', n_ch),
                crs.color_pair(2) if c else crs.A_UNDERLINE)

            y += 1

            for artist in content['artists']:  # Write each artist.
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)
                    
                self.main.addstr(
                    y, n_start, CrsWriter.trunc(artist['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)
                    
                y += 1
                i += 1

        if 'albums' in content and content['albums']:  # Albums header.
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if c else crs.A_UNDERLINE)
            self.main.addstr(
                y, n_start, CrsWriter.trunc('Album', n_ch),
                crs.color_pair(2) if c else crs.A_UNDERLINE)
            self.main.addstr(
                y, ar_start, CrsWriter.trunc('Artist', ar_ch),
                crs.color_pair(2) if c else crs.A_UNDERLINE)

            y += 1

            for album in content['albums']:  # Write each album.
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)
                self.main.addstr(
                    y, n_start, CrsWriter.trunc(album['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)
                self.main.addstr(
                    y, ar_start, CrsWriter.trunc(album['artist'], ar_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if c else 0)
                    
                y += 1
                i += 1

        self.main.refresh()


# ------------------------- CRSWRITER END ------------------------- #

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
    if content is None:
        out.now_playing()

    try:
        command, arg = input.split(maxsplit=1)
    except ValueError:  # No argument.
        command = input

    if command in commands:
        commands[command](arg)
        if content is not None:
            out.display()
    else:
        out.error_msg('Nonexistent command.')


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
    total = sum([len(content[k]) for k in content.keys])
    if num < 0 or num > total:
        out.error_msg('Index out of range: valid between 1-%d.' % total)
        return None

    i = 1
    for key in ('songs', 'artists', 'albums'):  # Hardcoded to guarantee order.
        for item in content[key]:
            if i == num:
                return item.fill(limit)  # Always return item with all content.
            else:
                i += 1


def enqueue(arg=None):
    """
    Display the current queue, or add an item to the queue. Can update content.

    Keyword arguments:
    arg=None: Index of the MusicObject in the main window to add to
      the queue, 'c' to clear the queue, None to display the queue, or
      a space-delimited list of indices to add to the queue, i.e. '1 2 3'.
    """
    global content

    if arg is None:
        if not queue:  # Nothing to display.
            out.error_msg('The queue is empty.')

        else:  # Display the queue.
            content = queue.collect()

    elif content is None:  # Nothing to queue.
        out.error_msg('Wrong context for queue.')

    else:
        if arg is 'c':  # Clear the queue.
            out.outbar_msg('Cleared queue.')
            queue.clear()

        else:
            try:
                num = int(arg)

            except ValueError:
                try:  # Check for multi-option argument.
                    nums = [int(i) for i in arg.split()]
                except ValueError:  # Invalid argument.
                    out.error_msg('Invalid argument to queue.')
                else:  # Add all arguments to the queue.
                    items = [get_option(num) for num in nums]
                    count = queue.extend(
                        [item for item in items if item is not None])
                    out.outbar_msg('Added %d songs%s to the queue.' %
                           (count, '' if count == 1 else 's'))

            else:
                item = get_option(num)
                if item is not None:
                    if item['kind'] == 'artist':  # Artists can't be queued.
                        out.error_msg(
                            'Can only add songs or albums to the queue.')

                    else:
                        queue.append(item)
                        out.outbar_msg('Added \'%s\' to the queue.' %
                                       item.to_string())


def expand(num=None):
    """
    Display all of a MusicObject's information: songs, artists, and albums.
      Can update content.

    Keyword arguments:
    num=None: Index of the MusicObject in the main window to be expanded.
    """
    global content

    if num is None:  # No argument.
        out.error_msg('Missing argument to play.')
    elif content is None:  # Nothing to expand.
        out.error_msg('Wrong context for expand.')
    else:
        try:
            num = int(num)
        except ValueError:  # num needs to be an int.
            out.error_msg('Invalid argument to play.')
        else:
            if out.disable:
                limit = -1
            else:
                limit = int((main.getmaxyx()[0] - 6)/3)
            opt = get_option(num, limit)

            if opt is not None:  # Valid input.
                content = opt.collect(limit=limit)
                outbar.erase()
                outbar.refresh()


def help(arg=0):
    """
    Display basic pmcli commands. Changes content.

    Keyword arguments:
    arg=0: Irrelevant.
    """
    global content
    content = None
    if out.disable:
        return

    # Don't use generic addstr() because we don't want to call trunc() here.
    main.erase()
    self.main.addstr(
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


def play(arg=None):
    """
    Play a MusicObject or the current queue. Can change content.

    Keyword arguments:
    arg=None: A number n to play item n, 's' to play the queue in shuffle mode,
      or None to play the current queue in order.
    """
    global content

    if arg is None or arg is 's':
        if not queue:  # Can't play an empty queue.
            out.error_msg('The queue is empty.')
        else:  # Play the queue.
            if arg is 's':  # Shuffle.
                queue.shuffle()
            content = queue.collect()
            out.display()
            out.outbar_msg('[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
            queue.play()
            if not out.disable:
                outbar.erase()  # Remove trailing output.
                outbar.refresh()

    elif content is None:  # Nothing to play.
        out.error_msg('Wrong context for play.')
    else:
        try:
            num = int(arg)
        except ValueError:  # arg needs to be an int if it isn't 's'.
            out.error_msg('Invalid argument to play.')
        else:
            opt = get_option(num)

            if opt is not None:  # Valid input.
                out.outbar_msg('[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
                opt.play()
                out.addstr(infobar, 'Now playing: None')
                if not out.disable:  # Remove trailing output.
                    outbar.erase()
                    outbar.refresh()


def restore(fn=None):
    """
    Restore queue from a file.

    Keyword arguments:
    fn=None: Name of the file containing the playlist.
      File should be at ~/.local/share/pmcli/playlists/.
    """
    path = join(expanduser('~'), '.local', 'share', 'pmcli', 'playlists')
    if fn is None:  # No argument.
        out.error_msg('Missing argument to restore.')
    elif not exists(join(path, fn)):  # Playlist file doesn't exist.
        out.error_msg('%s does not exist.' % fn)
    else:
        out.outbar_msg('Restoring queue from %s...' % fn)
        try:  # Read the playlist.
            with open(join(path, fn)) as f:
                json_songs = json.load(f)
        except json.decoder.JSONDecodeError:  # Bad file.
            out.error_msg('%s is not a valid playlist file.' % fn)
        else:
            songs = [Song(song, source='json')
                     for song in json_songs if song.verify()]

            # Replace the current queue with the playlist.
            del queue[:]
            del queue.ids[:]
            queue.extend(songs)
            out.outbar_msg('Restored %d/%d songs from playlist %s.' %
                           (len(songs), len(json_songs), fn))


def search(query=None):
    """
    Search Google Play Music for a given query. Changes content.

    Keyword arguments:
    query=None: The search query.

    Returns: A dict of lists with keys 'songs', 'artists', and 'albums'.
    """
    global content

    if query is None:  # No argument.
        out.error_msg('Missing search query.')
        return

    # Fetch as many results as we can display depending on terminal height.
    if not out.disable:
        limit = int((main.getmaxyx()[0] - 3)/3)
    else:
        limit = -1

    out.outbar_msg('Searching for \'%s\'...' % query)
    result = api.search(query, max_results=limit)
    if not out.disable:
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
    iters = [iter(result[mapping[k]['hits']]) for k in content.keys()]

    # Create 'limit' of each type.
    for i in range(limit):
        for k in content.keys():
            try:
                content[k].append(
                    mapping[k]['class'](next(iters[k])[mapping[k]['key']]))
            except StopIteration:
                del iters[k]

    return content


def write(fn=None):
    """
    Write the current queue to a file.

    Keyword arguments:
    fn=None: File to be written to.
      File is stored at ~/.local/share/pmcli/playlists/.
    """
    path = join(expanduser('~'), '.local', 'share', 'pmcli', 'playlists')
    if not queue:  # Can't save an empty queue.
        out.error_msg('Queue is empty.')
    elif fn is None:  # No argument.
        out.error_msg('Missing argument to write.')
    elif not exists(path):  # No playlists directory.
        out.error_msg('Path to playlists does not exist.')
    elif exists(join(path, fn)):  # Playlist alreadt exists at path/fn.
        out.error_msg('Playist %s already exists.' % fn)
    else:  # Write the playlist.
        with open(join(path, fn), 'a') as f:
            json.dump(queue, f)
        out.outbar_msg('Wrote queue to %s.' % fn)




# ------------------------- LOGIN STUFF START ------------------------- #

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
    set_colours(config['colour'])
    main.bkgdset(' ', crs.color_pair(1))
    inbar.bkgdset(' ', crs.color_pair(1))
    infobar.bkgdset(' ', crs.color_pair(2))
    outbar.bkgdset(' ', crs.color_pair(4))


def validate_config(config):
    """
    Verify that a config file has all necessary data.
      If the check fails, the program ends.

    Arguments:
    config: Config to be checked.

    Returns: Whether or not the config file has colour support.
    """
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

    if not user_valid or colours_valid:
            out.goodbye('Invalid config file, please refer to '
                        'config.example: Exiting.')

    return colours_valid

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
        if out.disable:
            try:
                config['user']['password'] = getpass()
            except KeyboardInterrupt:
                out.goodbye('Exiting.')
        else:
            crs.noecho()  # Don't show the password as it's entered.
            out.addstr(inbar, 'Enter your password: ')
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

def login(user):
    """
    Log into Google Play Music. Succeeds or exits.

    Arguments:
    user: Dict containing auth information.
    """
    if not api.login(user['email'], user['password'], user['deviceid']):
        out.goodbye('Login failed: Exiting.')
    out.addstr(outbar, 'Logged in as %s.' % user['email'])  # Login succeeded.


if __name__ == '__main__':
    main, inbar, infobar, outbar = get_windows()
    out = CrsWriter(main, inbar, infobar, outbar)
    config = password(read_config())
    colour = validate_config(config)
    if colour:
        set_colours(config['colour'])
        out.colour = True
    out.addstr(infobar, 'Enter \'h\' or \'help\' if you need help.')
    login(config['user'])
    queue = Queue()
    global content
    content = None

    while True:
        pass
        # transition(out.get_input())
