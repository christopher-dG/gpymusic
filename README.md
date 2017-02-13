# pmcli – (p)lay (m)usic for (cli)
Browse and stream Google Play Music from a Linux terminal, thanks to [gmusicapi](https://github.com/simon-weber/gmusicapi)

## Note: pmcli is currently being rewritten in [develop](https://github.com/christopher-dg/pmcli/tree/develop) with tons of improvements!

### Dependencies 
pmcli depends on Python 3, `mpv`, and `gmusicapi`.

### Setup
- `git clone https://github.com/christopher-dG/pmcli`
- `cd pmcli`
- `mkdir -p ~/.config/pmcli`
- `cp config mpv_input.conf ~/.config/pmcli`

If you just want to run the program locally, you can stop here. If you wish to install:
- `cp -r pmcli /etc/`
- `chmod +x /etc/pmcli/pmcli.py`
- `ln -s /etc/pmcli/pmcli.py /usr/local/bin/pmcli`

Don't forget to manually edit your config file in `~/.config/pmcli`!

### Getting your device ID
To find a valid device ID, configure email and password in `config`, and then run `python get_dev_id.py` to print out a list of IDs for you to try.

### Running `pmcli`
Running locally: 
- `cd pmcli/pmcli`
- `python pmcli.py`

Installed:
- `pmcli`

Note: If your python 3 binary is not located at `/usr/bin/python`, you will need to edit the first line of `pmcli.py`. 

### Controls
- `h/help`: print help
- `s/search` query: search for query
- `i/info` 123: expand item number 123
- `p/play` 123: play item number 123
- `q/quit`: exit pmcli

When playing music:

- `9/0`: volume down/up
- `spc`: play/pause
- `n`: next track
- `q`: stop

### Todo, when I have time and motivation (not ordered by priority):
- seek backwards function
- playlist support
- a pretty-looking ncurses UI, colour themes
- option to go back to previous state
- shuffle functionality
- more specific search (artists only, etc.)
- genres
- save music locally
- cache api results for shorter loads
- format for pip, upload to PyPI
