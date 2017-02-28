from music_objects import MusicObject, Song
import consts


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
        elif item['kind'] in ('song', 'libsong'):
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
        return sum(self.append(item) for item in items)

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
        l = len(cache)
        # Wow, this got really ugly thanks to libraries ._.
        if cache[0]['kind'] == 'libsong':  # Playing library songs.
            for i in range(l):
                s = cache.pop(0)
                consts.w.now_playing('(%d/%d) %s (%s)' %
                                     (i + 1, l, str(s), s['time']))
                if s.play() is 11:
                    self.extend(cache)
                    break

        else:  # Streaming songs.
            index = MusicObject.play(cache)
            self.extend(cache[index:])
        consts.w.now_playing()
        consts.w.erase_outbar()

    def restore(self, json):
        songs = [
            Song(song, source='json')
            for song in json if Song.verify(song)
        ]
        del self[:]
        self.extend(songs)
        consts.w.outbar_msg('Restored %d songs from playlist.' % len(self))
