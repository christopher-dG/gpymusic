from gmusicapi import Musicmanager
from music_objects import LibrarySong
import consts
import json
import zipfile
from os.path import expanduser, isfile, join


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
        path = join(expanduser('~'), '.local', 'share', 'pmcli', 'library.zip')
        if not isfile(path):
            return False
        # Todo: Inform the user about what went wrong before regenerating.
        try:
            with zipfile.ZipFile(path) as z:
                try:
                    lib = json.loads(z.read('library.json'))
                except json.JSONDecodeError:  # The .json file is invalid.
                    return False
        except zipfile.BadZipFile:  # The .zip file is invalid.
            return False

        for key in lib:
            for item in lib[key]:
                try:
                    self[key].append(consts.mapping[key]['cls']
                                     (item, source='json'))
                except KeyError:  # The file has the wrong data.
                    return False

        return True

    def gen_library(self):
        for song in self.mm.get_uploaded_songs():
            self['songs'].append(LibrarySong(song))
        for song in self.mm.get_purchased_songs():
            self['songs'].append(LibrarySong(song))
        # Save the zip with writestr.

    def search(self, query):
        """
        Search the library for some query. and update the
          view with the results.

        Keyword arguments:
        query=None: The search query.
        """
        if query is None:
            consts.w.error_msg('Missing search query')
            return

        if consts.w.curses:
            limit = int((consts.w.main.getmaxyx()[0] - 3) / 3)
        else:
            limit = 50
        consts.w.outbar_msg('Searching for \'%s\'...' % query)
        consts.v.clear()
        count = 0
        for song in self['songs']:
            if any(query in song[k] for k in ('name', 'artist', 'album')):
                count += 1
                consts.v['songs'].append(song)
                if count == limit:
                    break

    def play(arg=None):
        pass
