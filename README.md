# Google Py Music

## A standalone terminal client for Google Play Music

Browse and stream Google Play Music from the comfort and familiarity of your favourite terminal.

![screencast](https://fat.gfycat.com/MixedCoordinatedAmphibian.gif "Just pretend that this says Google Py Music instead of pmcli.")

## Dependencies

- [Python 3](https://python.org/downloads)
- [mpv](https://mpv.io)
- [gmusicapi](https://github.com/simon-weber/gmusicapi): `pip install gmusicapi`
  - Note: If you have both Python 2 and 3 installed, specify Python 3 with `pip3 install gmusicapi`.

## Installing, updating and uninstalling

Use the `.sh` scripts in `script` to install, update or remove the program. Note that they require root access; while I assure you they're safe, it's good practice to read the scripts so that you know what they do before running them.

## Running Google Py Music

Once installed, the program can be run from the terminal with `gpymusic`. While the program is running, don't resize your terminal.

## Accounts

Google Py Music works similiarly to the web interface in that users with free accounts can only arbitrarily access music that they've purchased or uploaded, whereas users with free accounts can search for and stream anything. When playing music with a free account, the entire song is downloaded and played locally rather than streamed.

Notes for free users:

- A one-time OAuth sign-in is required for free users, run `script/oauth_login.py` and follow the prompts to authorize.
- If you don't want to wait for songs to download on the fly, you can download them all in one go with `script/download_all.py`. Songs are stored in `~/.local/share/gpymusic/songs`.
- The `e/expand` command does not work for free users because artists and albums cannot be generated, so there is nothing for it to do.
- I don't have enough music uploaded to my free account to properly test it, so please [open issues](https://github.com/christopher-dG/gpymusic/issues/new) about any crashes or other problems.

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
- `Ctrl-C`: Exit Google Py Music

When playing music:

- `spc`: Play/pause
- `9/0`: Volume down/up (Note: volume changes are not persistent across songs, so I recommend you adjust your system volume instead)
- `n`: Next track
- `q`: Stop
- `↑/↓/←/→`: Seek

## Colours

Colour themes are defined in the `colour` section of your config file. To enable colour, make sure `enable` is set to `yes` and set the fields to hex colours as desired. `highlight` affects the section headers and 'now playing' output, `content{1|2}` affect the main window, and `background` and `foreground` are self-explanatory.

Note: Upon exiting the program, your terminal colours will likely be modified. Just open a new terminal session and your colours will be back to normal.

## Device ID

If you don't know your device ID, run `script/get_dev_id.py` and answer the prompts to generate a list of valid device IDs.

## Password

You can choose to leave the password field empty as it is in `config.example`, and you will be prompted for it upon starting the program. Otherwise, you can supply it for automatic logins.

**If you store your password in plain text, be aware the potential consequences.**

## 2-Factor Authentication

If your account has 2FA set up, you will need to use an [app password](https://support.google.com/accounts/answer/185833?hl=en) to log in. If you're storing your password in your config file, replace it with the app password.

## Crashes

If `gpymusic` crashes, your terminal settings will likely be messed up, in which case `stty sane` will restore order. Don't forget to [open an issue](https://github.com/christopher-dG/gpymusic/issues/new)!

### Disclaimer
Expect bugs, and please report them! I hope you enjoy using Google Py Music, and if you don't, that's okay too because I enjoy working on it.
