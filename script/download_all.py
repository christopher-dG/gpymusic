#! /usr/bin/env python3

from gmusicapi import Musicmanager
from os.path import expanduser, join

mm = Musicmanager()
if not mm.login():
    print('Login failed: did you run oauth_login.py?')
    quit()

# No point properly checking for duplicates when overwriting them
# gives the same result.
songs = {}
for song in mm.get_purchased_songs():
    songs[song['id']] = ' - '.join(
        [song['title'], song['artist'], song['album']]
    )
for song in mm.get_uploaded_songs():
    songs[song['id']] = ' - '.join(
        [song['title'], song['artist'], song['album']]
    )

print('Downloading %d songs to ~/.local/share/pmcli/songs. '
      'This might take a while...' % len(songs))
i = 1
for id in songs:
    print('%d/%d: %s' % (i, len(songs), songs[id]))
    with open(join(expanduser('~'), '.local', 'share', 'pmcli',
                   'songs', '%s.mp3') % songs[id], 'wb') as f:
        f.write(mm.download_song(id)[1])
    i += 1
