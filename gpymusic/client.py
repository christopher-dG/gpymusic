from . import common
from . import music_objects

import json
import zipfile

from os.path import exists, isfile, join
from random import shuffle

from gmusicapi import Musicmanager


class Client:
    """Driver for most of gpymusic's functionality."""

    def transition(self, input=""):
        """
        Route input to the appropriate function.

        Keyword arguments:
        input="": predefined user input. If not set, prompt for input.
        """
        commands = {
            'h': self.help,
            'help': self.help,
            'e': self.expand,
            'expand': self.expand,
            's': self.search,
            'search': self.search,
            'p': self.play,
            'play': self.play,
            'q': self.queue,
            'queue': self.queue,
            'w': self.write,
            'write': self.write,
            'r': self.restore,
            'restore': self.restore,
        }

        arg = None
        if common.v.is_empty():
            common.w.addstr(
                common.w.infobar,
                'Enter \'h\' or \'help\' if you need help.'
            )
        else:
            common.w.now_playing()

        user_input = common.w.get_input() if not input else input
        try:
            command, arg = (s.strip() for s in user_input.split(maxsplit=1))
        except ValueError:  # No argument.
            command = user_input.strip()

        if command in commands:
            commands[command](arg)
            common.w.display()
        else:
            common.w.error_msg('Nonexistent command')

    def help(self, arg=0):
        """
        Display basic gpymusic commands.

        Keyword arguments:
        arg=0: Irrelevant.
        """
        common.v.clear()
        if not common.w.curses:
            return

        common.w.main.erase()
        common.w.main.addstr(
        """
        Commands:
        s/search search-term: Search for search-term
        e/expand 123: Expand item number 123
        p/play: Play the current queue
        p/play s: Shuffle and play the current queue
        p/play 123: Play item number 123
        q/queue: Show the current queue
        q/queue 123: Add item number 123 to the queue
        q/queue 1 2 3: Add items 1, 2, and 3 to the queue
        q/queue c: Clear the current queue
        w/write playlist-name: Write current queue to playlist playlist-name
        r/restore playlist-name: Replace the current queue with a playlist
        h/help: Show this help message
        Ctrl-C: Exit gpymusic
        """  # noqa
        )
        common.w.main.refresh()

    def write(self, fn=None):
        """
        Write the current queue to a file.

        Keyword arguments:
        fn=None: File to be written to.
          File is stored at ~/.local/share/gpymusic/playlists/.
        """
        path = join(common.DATA_DIR, 'playlists')
        if not common.q:  # Can't save an empty queue.
            common.w.error_msg('Queue is empty')
        elif fn is None:  # No filename specified.
            common.w.error_msg('Missing argument to write')
        elif not exists(path):  # No playlists directory.
            common.w.error_msg('Path to playlists does not exist')
        elif exists(join(path, fn)):  # Playlist already exists at path/fn.
            common.w.error_msg('Playist %s already exists' % fn)

        else:  # Write the playlist.
            with open(join(path, fn), 'w') as f:
                json.dump(common.q, f)
            common.w.outbar_msg('Wrote queue to %s.' % fn)

    def restore(self, fn=None):
        """
        Restore queue from a file.

        Keyword arguments:
        fn=None: Name of the file containing the playlist.
          File should be at ~/.local/share/gpymusic/playlists/.
        """
        path = join(common.DATA_DIR, 'playlists')
        if fn is None:  # No filename specified.
            common.w.error_msg('Missing argument to restore')
        elif not isfile(join(path, fn)):  # Playlist file doesn't exist.
            common.w.error_msg('Playlist %s does not exist' % fn)

        else:
            common.w.outbar_msg('Restoring queue from %s...' % fn)
            try:  # Read the playlist.
                with open(join(path, fn)) as f:
                    json_songs = json.load(f)
            except json.decoder.JSONDecodeError:  # Bad file.
                common.w.error_msg('%s is not a valid playlist file' % fn)
            else:
                common.q.restore(json_songs)

    def queue(self, arg=None):
        """
        Display the current queue, or add an item to the queue.

        Keyword arguments:
        arg=None: Index of the MusicObject in the main window to add to
          the queue, 'c' to clear the queue, None to display the queue, or
          a space-delimited list of indices to add to the queue, i.e. '1 2 3'.
        """
        if arg is None:
            if not common.q:  # Nothing to display.
                common.w.error_msg('The queue is empty')

            else:  # Display the queue.
                if common.w.curses:
                    # Allow room for header.
                    limit = common.w.ylimit - 2
                else:
                    limit = -1
                common.v.replace(common.q.collect(limit))

            return

        if arg in ('c', 'C'):  # Clear the queue.
            del common.q[:]
            common.w.outbar_msg('Cleared queue.')
            return

        if common.v.is_empty():
            common.w.error_msg('Wrong context for queue')
            return

        try:
            num = int(arg)
        except ValueError:
            try:  # Check for multi-option argument.
                nums = [int(i) for i in arg.split()]
            except ValueError:  # Invalid argument.
                common.w.error_msg('Invalid argument to queue')

            else:  # Add all arguments to the queue.
                common.w.outbar_msg('Adding items to the queue...')
                items = [self.get_option(num) for num in nums]
                count = common.q.extend(
                    [item for item in items if item is not None]
                )
                common.w.outbar_msg(
                    'Added %d song%s to the queue.' %
                    (count, '' if count is 1 else 's')
                )

        else:
            if (
                    num > len(common.v['songs']) and
                    num <= len(common.v['songs']) + len(common.v['artists'])
            ):
                common.w.error_msg(
                    'Can only add songs or albums to the queue.'
                )

            else:
                item = self.get_option(num)
                if item is not None:
                    count = common.q.append(item)
                    common.w.outbar_msg(
                        'Added %d song%s to the queue.' %
                        (count, '' if count is 1 else 's')
                    )

    def get_option(self, num, limit=-1):
        """
        Select a numbered MusicObject from the main window.

        Arguments:
        num: Index of the MusicObject in the main window to be returned.

        Keyword argumnents:
        limit=-1: Number of songs to generate for artists,
          determined by terminal height.

        Returns: The MusicObject at index 'num'.
        """
        total = sum(len(common.v[k]) for k in common.v.keys())
        if num < 0 or num > total:
            common.w.error_msg(
                'Index out of range: valid between 1-%d' % total
            )
            return None

        i = 1
        for key in ('songs', 'artists', 'albums'):  # Guarantee order.
            for item in common.v[key]:
                if i == num:
                    # Return item with as much content as we can display.
                    item.fill(
                        music_objects.mapping[item['kind'] + 's']['lookup'],
                        limit
                    )
                    return item
                else:
                    i += 1

    def play(self, arg=None):
        """
        Play a MusicObject or the current queue.

        Keyword arguments:
        arg=None: n to play item n, 's' to play the queue in shuffle mode,
          or None to play the current queue in order.
        """
        if arg is None or arg in ('s', 'S'):
            if not common.q:  # Can't play an empty queue.
                common.w.error_msg('The queue is empty')
            else:  # Play the queue.
                if arg is 's':  # Shuffle.
                    shuffle(common.q)
                if common.w.curses:
                    # Allow room for header.
                    limit = common.w.ylimit - 1
                else:
                    limit = -1
                    common.v.replace(common.q.collect(limit))
                common.w.display()
                common.w.outbar_msg(
                    '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
                common.q.play()
            return

        if common.v.is_empty():  # Nothing to play.
            common.w.error_msg('Wrong context for play')
            return

        try:
            num = int(arg)
        except ValueError:  # arg needs to be an int if it isn't 's'.
            common.w.error_msg('Invalid argument to play')

        else:
            item = self.get_option(num)

            if item is not None:  # Valid input.
                common.w.outbar_msg(
                    '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek'
                )
                if item['kind'] == 'libsong':  # This is hacky and bad.
                    common.w.now_playing(
                        '(1/1) %s (%s)' % (str(item), item['time'])
                    )
                item.play()
                common.w.now_playing()
                common.w.erase_outbar()


class FreeClient(Client):
    """
    Client for free users with limited functionality.
      Free users only have access to songs that they have either purchased
      or uploaded, and they must be downloaded before they can be played.
      Artists and albums cannot be generated, so the expand method has no use.
    """
    def __init__(self):
        """
        Log into Musicmanager and get the library, either by loading an
          existing library file, or by generating a new one.
        """
        self.kind = 'free'
        self.mm = Musicmanager()
        self.mm.login()
        self.songs = []
        self.load_library()
        if not self.songs:
            self.gen_library()

    def load_library(self):
        path = join(common.DATA_DIR, 'library.zip')
        common.w.outbar_msg('Loading library...')
        if not isfile(path):
            common.w.addstr(common.w.infobar, 'Could not find library file.')
            return
        try:
            with zipfile.ZipFile(path) as z:
                try:
                    lib = json.loads(z.read('library.json').decode('utf-8'))
                except json.JSONDecodeError:  # The .json file is invalid.
                    common.w.addstr(
                        common.w.infobar, 'Library file is corrupt.'
                    )
                    return
        except zipfile.BadZipFile:  # The .zip file is invalid.
            common.w.addstr(common.w.infobar, 'Library file is corrupt.')
            return

        for item in lib['songs']:
            try:
                self.songs.append(
                    music_objects.LibrarySong(item, source='json'))
            except KeyError:  # The file has the wrong data.
                common.w.addstr(common.w.infobar, 'Library file is corrupt.')
                return

        l = len(self.songs)
        common.w.outbar_msg('Loaded %s song%s.' % (l, '' if l is 1 else 's'))

    def gen_library(self):
        ids = []  # Avoid duplicates between purchased and uploaded songs.
        common.w.outbar_msg('Generating your library...')

        for song in self.mm.get_uploaded_songs():
            if song['id'] not in ids:
                self.songs.append(music_objects.LibrarySong(song))
                ids.append(song['id'])
        for song in self.mm.get_purchased_songs():
            if song['id'] not in ids:
                self.songs.append(music_objects.LibrarySong(song))
                ids.append(song['id'])
        # Todo: Use something other than json for library storage since it
        # doesn't really make logical sense (songs is a list, not a dict),
        # but for now it's very easy to use.
        with zipfile.ZipFile(join(common.DATA_DIR, 'library.zip'), 'w') as z:
            z.writestr('library.json', json.dumps({'songs': self.songs}))
        l = len(self.songs)
        common.w.outbar_msg(
            'Generated %d song%s.' % (l, '' if l is 1 else 's')
        )
        common.w.now_playing()

    def expand(self, arg=None):
        """
        Artists/albums cannot be generated. so free users cannot expand songs..

        Keyword arguments:
        arg=None: Irrelevant.
        """
        common.q.error_msg('Free users cannot use expand')

    def search(self, query):
        """
        Search the library for some query. and update the
          view with the results.

        Keyword arguments:
        query=None: The search query.
        """
        if query is None:
            common.w.error_msg('Missing search query')
            return

        # Save the current view in case there are no results.
        cache = common.v.copy()

        if common.w.curses:
            limit = common.w.main.ylimit - 4
        else:
            limit = 10
        common.w.outbar_msg('Searching for \'%s\'...' % query)
        common.v.clear()
        count, query = 0, query.lower()  # Search is case-insensitive.
        for song in self.songs:
            if any(query in song[k].lower()
                   for k in ('name', 'artist', 'album')):
                count += 1
                common.v['songs'].append(song)
                if count == limit:
                    break
        common.w.outbar_msg('Search returned %d results.' % len(common.v))

        if common.v.is_empty():
            common.v.replace(cache)


class FullClient(Client):
    """Client for paid account users with full functionality."""
    def __init__(self):
        self.kind = 'full'

    def expand(self, num=None):
        """
        Display all of a MusicObject's information: songs, artists, and albums.

        Keyword arguments:
        num=None: Index of the MusicObject in the main window to be expanded.
        """
        if not common.mc.is_subscribed:
            common.w.error_msg('Free users cannot expand songs')
            return
        if num is None:  # No argument.
            common.w.error_msg('Missing argument to play')
            return
        if common.v.is_empty():  # Nothing to expand.
            common.w.error_msg('Wrong context for expand')
            return

        try:
            num = int(num)
        except ValueError:  # num needs to be an int.
            common.w.error_msg('Invalid argument to play')
        else:
            # Artists only have one artist and albums only have one album,
            # so we can allocate more space for the other fields.
            limit = int((common.w.ylimit - 9) / 2) if common.w.curses else -1
            item = self.get_option(num, limit)

            if item is not None:  # Valid input.
                common.v.replace(item.collect(limit=limit))
                common.w.erase_outbar()

    def search(self, query=None):
        """
        Search Google Play Music for a given query and update the
          view with the results.

        Keyword arguments:
        query=None: The search query.
        """
        if query is None:  # No argument.
            common.w.error_msg('Missing search query')
            return

        # Save the current view in case there are no results.
        cache = common.v.copy()

        # Fetch as many results as we can display depending on terminal height.
        if common.w.curses:
            limit = int((common.w.ylimit - 3) / 3)
        else:
            limit = 50

        common.w.outbar_msg('Searching for \'%s\'...' % query)
        result = common.mc.search(query, max_results=limit)
        common.w.erase_outbar()

        # 'class' => class of MusicObject
        # 'hits' => key in search result
        # 'rslt_key' => per-entry key in search result
        common.v.clear()
        iters = {k: iter(result[music_objects.mapping[k]['hits']])
                 for k in common.v.keys()}
        # Create at most 'limit' of each type.
        for i in range(limit):
            for k in iters.keys():
                try:
                    common.v[k].append(music_objects.mapping[k]['cls'](
                        next(iters[k])[music_objects.mapping[k]['rslt_key']]))
                except StopIteration:
                    pass
        common.w.outbar_msg('Search returned %d results.' % len(common.v))

        if common.v.is_empty():
            common.v.replace(cache)
