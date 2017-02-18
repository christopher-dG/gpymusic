# pmcli - (p)lay (m)usic for (cli)

<<<<<<< HEAD
## Note: pmcli is currently being rewritten in [develop](https://github.com/christopher-dg/pmcli/tree/develop) with tons of improvements!

### Dependencies 
pmcli depends on Python 3, `mpv`, and `gmusicapi`.
=======
Browse and stream Google Play Music from the command line
>>>>>>> develop

## Dependencies

- [Python 3](https://www.python.org/downloads/)
- [mpv](mpv.io)
- [gmusicapi](https://github.com/simon-weber/gmusicapi): `pip install gmusicapi`

## Installation

```sh
git clone https://github.com/christopher-dG/pmcli
cd pmcli
```

Now, edit `config` with your Google account information. Next:

```sh
mkdir -p ~/.config/pmcli ~/.local/share/pmcli/playlists
cp config mpv_input.conf ~/.config/pmcli
cp -r src ~/.local/share/pmcli
chmod +x ~/.local/share/pmcli/src/pmcli.py
ln -s ~/.local/share/pmcli/src/pmcli.py /usr/local/bin/pmcli
```

## Device ID

If you don't know your device ID, run `python script/get_dev_id.py` and answer the prompts to generate a list of valid device IDs.

## Running pmcli

Once installed, the program can be run with `pmcli`.

## Controls

- `s/search search-term`: Search for 'search-term'`
- `e/expand 123`: Expand item number 123
- `p/play`: Play current queue
-  `p/play s`: Shuffle and play current queue
- `p/play 123`: Play item number 123
- `q/queue`: Show current queue
- `q/queue 123`:  Add item number 123 to queue
- `w/write file-name`: Write current queue to file file-name
- `r/restore file-name`: Replace current queue with playlist from file-name
- `h/help`: Show help message
- `Ctrl-C`: Exit pmcli

When playing music:

- `spc`: Play/pause
- `9/0`: Volume down/up (Note: volume changes do not persist across songs, so I recommend you adjust your system volume instead)
- `n`: Next track
- `q`: Stop

### Todo

- list playlists command
- Properly display shuffled queue
- Restore queue from shuffle
- Seek backwards function
- Colour support
- Text-only debugging UI
- Add threading support (play in background and keep browsing)
- Caching queue contents for seamless transitions (save locally and delete after? Probably needs threading)
