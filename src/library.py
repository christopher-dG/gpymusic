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
        if not self.mm.login():  # How to hide warning?
            self.mm.perform_oauth()
            self.mm.login()
        self['songs'] = []
        self.load_library() or self.gen_library()

    def load_library(self):
        path = join(consts.DATA_DIR, 'library.zip')
        consts.w.outbar_msg('Loading library...')
        if not isfile(path):
            return False
        # Todo: Inform the user about what went wrong before regenerating.
        try:
            with zipfile.ZipFile(path) as z:
                try:
                    lib = json.loads(z.read('library.json').decode('utf-8'))
                except json.JSONDecodeError:  # The .json file is invalid.
                    return False
        except zipfile.BadZipFile:  # The .zip file is invalid.
            return False

        for item in lib['songs']:
            try:
                self['songs'].append(consts.mapping['libsongs']['cls'](item))
            except KeyError:  # The file has the wrong data.
                return False

        return True

    def gen_library(self):
        ids = []
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
            limit = int((consts.w.main.getmaxyx()[0] - 3) / 3)
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
                i = 1
                for song in consts.q:
                    consts.w.now_playing(
                        '(%d/%d) %s (%s)' %
                        (i, len(consts.q), str(song), song['time']))
                    if song.play() == 11:
                        break
                    i += 1
            return
        if consts.v is None:  # Nothing to play.
            consts.w.error_msg('Wrong context for play')
            return

        try:
            num = int(arg)
        except ValueError:  # arg needs to be an int if it isn't 's'.
            consts.w.error_msg('Invalid argument to play.')
        else:
            item = get_option(num)

            if item is not None:  # Valid input.
                consts.w.outbar_msg(
                    '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
                item.play()
                consts.w.now_playing()
                consts.w.erase_outbar()
