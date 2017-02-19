# pmcli - (p)lay (m)usic for (cli)

Browse and stream Google Play Music from comfort and familiarity of your favourite terminal

![screencast]( https://zippy.gfycat.com/SnivelingLavishAtlanticblackgoby.gif "gfy")

## Notice
As of right now, pmcli only works for users with paid accounts (see [issue #5](https://github.com/christopher-dg/issue/5). In the next couple of days, I'll add the ability for free users to access their library, but searching/playing arbitrary stuff is not possible with gmusicapi in its current state.

## Dependencies

- [Python 3](https://python.org/downloads/)
- [mpv](https://mpv.io)
- [gmusicapi](https://github.com/simon-weber/gmusicapi): `pip install gmusicapi`

## Installation

```sh
git clone https://github.com/christopher-dG/pmcli
cd pmcli
mkdir -p ~/.config/pmcli ~/.local/share/pmcli/playlists
cp config.json config.example.json
cp config.json config.example.json mpv_input.conf ~/.config/pmcli
cp -r src ~/.local/share/pmcli
chmod +x ~/.local/share/pmcli/src/pmcli.py
sudo ln -s ~/.local/share/pmcli/src/pmcli.py /usr/local/bin/pmcli
```
Finally, you should edit `~/.config/pmcli/config.json` with your account information.

## Password

You can choose to leave the password field empty as it is in `config.example`, and you will be prompted for it upon starting the program. Otherwise, you can supply it for automatic logins.

**If you store your password in plain text, be aware the potential consequences.**

## Device ID

If you don't know your device ID, run `python get_dev_id.py` and answer the prompts to generate a list of valid device IDs.

## Running pmcli

Once installed, the program can be run with `pmcli`.

Note: Please, for your own sake, don't resize your terminal while the program is running.

## Controls

- `s/search search-term`: Search for 'search-term'
- `e/expand 123`: Expand item number 123
- `p/play`: Play current queue
- `p/play s`: Shuffle and play current queue
- `p/play 123`: Play item number 123
- `q/queue`: Show current queue
- `q/queue 123`:  Add item number 123 to queue
- `q/queue 1 2 3`:  Add items 1, 2, 3 to queue
- `q/queue c`:  Clear current queue
- `w/write file-name`: Write current queue to file file-name
- `r/restore file-name`: Replace current queue with playlist from file-name
- `h/help`: Show help message
- `Ctrl-C`: Exit pmcli

When playing music:

- `spc`: Play/pause
- `9/0`: Volume down/up (Note: volume changes do not persist across songs, so I recommend you adjust your system volume instead)
- `n`: Next track
- `q`: Stop
- `↑/↓/←/→`: Seek

## Colours

Colour themes are defined in the `[colour]` section of your config file. To enable colour, make sure `enable` is set to `yes` and set the fields to hex colours as desired. `highlight` affects the section headers and 'now playing' output, `content{1|2}` affect the main window, and `background` and `foreground` are self-explanatory.

Note: Upon exiting the program, your terminal colours will likely be modified. Just open a new terminal session and your colours will be back to normal.

## Uninstalling

You can uninstall `pmcli` with:

```sh
sudo rm -rf ~/.local/share/pmcli ~/.config/pmcli /usr/local/bin/pmcli
```

## Crashes

If `pmcli` crashes, your terminal settings will likely be messed up, in which case enter `stty sane` to restore order. And don't forget to file an issue!

## 2-Factor Authentication

If your account has 2FA set up, you will need to use an [app password](https://support.google.com/accounts/answer/185833?hl=en) to log in. If you're storing your password in your config file, replace it with the app password.

### Disclaimer
Expect bugs, and please report them! I hope you enjoy using pmcli, and if you don't, that's okay too because I enjoy working on it.
