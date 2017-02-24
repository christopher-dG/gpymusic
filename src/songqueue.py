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
        index = MusicObject.play(cache)
        consts.w.now_playing()
        self.extend(cache[index:])

    def restore(self, json):
        songs = [
            Song(song, source='json')
            for song in json if Song.verify(song)
        ]
        del self[:]
        self.extend(songs)
        consts.w.outbar_msg('Restored %d songs from playlist.' % len(self))
