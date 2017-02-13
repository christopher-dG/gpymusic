Important things that need doing:
- Guard against 'Now playing' output overflowing
- Guard against literally everything else's output overflowing
- Add song count in 'Now playing' output
- Enable queue restore from shuffle
- Get rid of really old output bar content (maybe show mpv keybindings while playing stuff instead)
- Maintain mpv volume across calls
- Center column titles
- Add padding between columns
- Properly hide sections if they have no content
- Rewrite the README when all these are done

Less important things to maybe do:
- Seek backwards function
- Text-only UI option (would be really nice for debugging non-curses related stuff)
- Save + restore playlists
- Add threading support (play in background and keep browsing)
- Get song length in now playing (and less urgently but very helpfully, show current time)
- Caching 'now playing' contents for seamless transitions (save locally and delete after? Probably needs threading)
