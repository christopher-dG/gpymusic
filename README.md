# pmcli
Stream Google Play Music from a Linux terminal, thanks to [gmusicapi](https://github.com/simon-weber/gmusicapi)

### Dependencies 
pmcli depends on `mpv` to play music and `gmusicapi` to access Google Play.

### Installation
- `git clone https://github.com/christopher-dG/pmcli`
- `cd pmcli`
- `./install.sh`

Don't forget to manually edit your config file in `~/.config/pmcli`.

### Getting your device ID
To find a valid device ID, configure email and password in `config`, and then run `python get_dev_id.py` to print out a list of IDs for you to try.

### Running
Simply run `pmcli` to launch.

### Controls
- `h/help`: print help
- `s/search` query: search for query
- `i/info` 123: expand item number 123
- `p/play` 123: play item number 123
- `q/quit`: exit pmcli

### Todo
- playlist support
- a pretty-looking ncurses UI, colour themes
- option to go back to previous state
- shuffle functionality
- more specific search (only artists, etc.)
- genres
- save music locally
- cache api results less loading