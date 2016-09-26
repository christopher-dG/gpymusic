# pmcli
Brows and stream Google Play Music from a Linux terminal, thanks to [gmusicapi](https://github.com/simon-weber/gmusicapi)

### Dependencies 
pmcli depends on `mpv` to play music and `gmusicapi` to access Google Play.

### Installation/Uninstallation
- `git clone https://github.com/christopher-dG/pmcli`
- `cd pmcli`
- `sudo ./install.sh`, or `sudo ./uninstall.sh`

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

When playing music:

- `9/0`: volume down/up
- `spc`: play/pause
- `n`: next track
- `q`: stop

No seek backwards function yet, sorry ._.

### Todo
- playlist support
- a pretty-looking ncurses UI, colour themes
- option to go back to previous state
- shuffle functionality
- more specific search (artists only, etc.)
- genres
- save music locally
- cache api results shorter loads
- format for pip, upload to PyPI

### License
The MIT License (MIT)
Copyright (c) 2016 Chris de Graaf

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.