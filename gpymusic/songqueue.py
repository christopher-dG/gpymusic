from . import common
from . import music_objects


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
          terminal height. -1 indicates no limit.

        Returns: A dict with key 'songs'.
        """
        return {
            'songs': self[:min(limit, len(self)) if limit != -1 else len(self)]
        }

    def play(self):
        """Play the queue. If playback is halted, restore unplayed items."""
        cache = self[:]
        del self[:]
        l = len(cache)
        if cache[0]['kind'] == 'libsong':  # Playing library songs.
            for i in range(l):
                s = cache.pop(0)
                common.w.now_playing(
                    '(%d/%d) %s (%s)' % (i + 1, l, str(s), s['time'])
                )
                common.v['songs'].pop(0)
                if s.play() is 11:
                    self.extend(cache)
                    break
                common.w.display()

        else:  # Streaming songs.
            index = music_objects.MusicObject.play(cache)
            self.extend(cache[index:])
        common.w.now_playing()
        common.w.erase_outbar()

    def restore(self, json):
        songs = [
            music_objects.mapping[song['kind'] + 's']['cls'](
                song, source='json'
            ) for song in json if music_objects.Song.verify(song)
        ]
        del self[:]
        self.extend(songs)
        common.w.outbar_msg('Restored %d songs from playlist.' % len(self))
