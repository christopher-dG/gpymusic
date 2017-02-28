from gmusicapi import Musicmanager
from music_objects import LibrarySong
from os.path import isfile, join
from pmcli import get_option
from random import shuffle
import consts
import view
import json
import zipfile


class Library(dict):
    """A Library contains a user's uploaded and purchased songs."""

    def __init__(self):
        """
        Login to the Musicmanager, and load an existing
          library or generate one.
        """
        self.mm = Musicmanager()
        if not self.mm.login():
            consts.w.erase_outbar()  # Why is this not working?
            consts.w.goodbye('Musicmanager login failed: did you run '
                             'oauth_login.py? Exiting.')
        self['songs'] = []
        self.load_library() or self.gen_library()

    def load_library(self):
        path = join(consts.DATA_DIR, 'library.zip')
        consts.w.outbar_msg('Loading library...')
        if not isfile(path):
            consts.w.addstr(consts.w.infobar, 'Could not find library file.')
            return False
        try:
            with zipfile.ZipFile(path) as z:
                try:
                    lib = json.loads(z.read('library.json').decode('utf-8'))
                except json.JSONDecodeError:  # The .json file is invalid
                    consts.w.addstr(consts.w.infobar,
                                    'Library file is corrupt.')
                    return False
        except zipfile.BadZipFile:  # The .zip file is invalid.
            consts.w.addstr(consts.w.infobar, 'Library file is corrupt.')
            return False

        for item in lib['songs']:
            try:
                self['songs'].append(
                    consts.mapping['libsongs']['cls'](item, source='json'))
            except KeyError:  # The file has the wrong data.
                consts.w.addstr(consts.w.infobar, 'Library file is corrupt.')
                return False

        l = len(self['songs'])
        consts.w.outbar_msg('Loaded %s song%s.' % (l, '' if l == 1 else 's'))
        return True

    def gen_library(self):
        ids = []
        consts.w.outbar_msg('Generating your library...')
        for song in self.mm.get_uploaded_songs():
            if song['id'] not in ids:
                self['songs'].append(LibrarySong(song))
                ids.append(song['id'])
        for song in self.mm.get_purchased_songs():
            if song['id'] not in ids:
                self['songs'].append(LibrarySong(song))
                ids.append(song['id'])
        with zipfile.ZipFile(join(consts.DATA_DIR, 'library.zip'), 'w') as z:
            z.writestr('library.json', json.dumps(self))
        l = len(self['songs'])
        consts.w.outbar_msg('Generated %d song%s.' %
                            (l, '' if l == 1 else 's'))

    def search(self, query):
        """
        Search the library for some query. and update the
          view with the results.

        Keyword arguments:
        query=None: The search query.
        """
        query = query.lower()
        if query is None:
            consts.w.error_msg('Missing search query')
            return

        if consts.w.curses:
            limit = consts.w.main.getmaxyx()[0] - 4
        else:
            limit = 50
        consts.w.outbar_msg('Searching for \'%s\'...' % query)
        if consts.v is not None:
            consts.v.clear()
        else:
            consts.v = view.View({'songs': [], 'artist': [], 'albums': []})
        count = 0
        query = query.lower()
        for song in self['songs']:
            if any(query in song[k].lower()
                   for k in ('name', 'artist', 'album')):
                count += 1
                consts.v['songs'].append(song)
                if count == limit:
                    break

    def play(self, arg=None):
        if arg is None or arg is 's':  # Play the queue.
            if not consts.q:
                consts.w.error_msg('The queue is empty')
            else:
                if arg is 's':  # Shuffle.
                    shuffle(consts.q)
                consts.w.outbar_msg(
                    '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
                consts.q.play()
            return
        if consts.v is None:  # Nothing to play.
            consts.w.error_msg('Wrong context for play')
            return

        try:
            num = int(arg)
        except ValueError:  # arg needs to be an int if it isn't 's'.
            consts.w.error_msg('Invalid argument to play.')
        else:
            item = get_option(num)  # This call will download the song.

            if item is not None:  # Valid input.
                consts.w.outbar_msg(
                    '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
                consts.w.now_playing(str(item))
                item.play()
                consts.w.now_playing()
                consts.w.erase_outbar()
