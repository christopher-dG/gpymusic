# Google Py Music

## A simple terminal client for Google Play Music

Browse and stream Google Play Music from the comfort and familiarity of your favourite terminal.

![screencast](https://fat.gfycat.com/MixedCoordinatedAmphibian.gif "Just pretend that this says Google Py Music instead of pmcli.")

## Dependencies

- [mpv](https://mpv.io)

## Installation

The easiest way to install is with `pip`, by running `pip install gpymusic` (use `pip3` if necessary).

You can also install from source:

```sh
$ git clone https://github.com/christopher-dG/gpymusic
$ cd gpymusic
$ python setup.py install  # Use python3 if necessary
```

A special thanks goes to [ftxrc](https://github.com/ftxrc) for his work on the `pip` installation.

## Configuration

Once `gpymusic` is installed, run `gpymusic-setup`. An example config file will be placed in `~/.config/gpymusic`.

### Colours

Colour themes are defined in the `colour` section of your config file. To enable colour, make sure `enable` is set to `yes` and set the fields to hex colours as desired. `highlight` affects the section headers and 'now playing' output, `content{1|2}` affect the main window, and `background`/`foreground` are self-explanatory.

**Note**: Upon exiting the program, your terminal colours will likely be modified. Just open a new terminal session and your colours will be back to normal.

### Device ID

If you don't know your device ID, run `gpymusic-get-dev-id` and follow the prompts to generate a list of valid device IDs.

### Password

You can choose to leave the password field empty and you will be prompted for it upon starting the program. Otherwise, you can supply it for automatic logins.

**If you store your password in plain text, be aware the potential consequences.**

## Running Google Py Music

Once installed and configured, the program can be run from the terminal with `gpymusic`. While the program is running, don't resize your terminal.

## Controls

- `s/search search-term`: Search for `search-term`
- `e/expand 123`: Expand item number `123`
- `p/play`: Play the current queue
- `p/play s`: Shuffle and play the current queue
- `p/play 123`: Play item number `123`
- `q/queue`: Show the current queue
- `q/queue 123`:  Add item number `123` to queue
- `q/queue 1 2 3`:  Add items `1`, `2`, and `3` to the queue
- `q/queue c`:  Clear the current queue
- `w/write file-name`: Write the current queue to file `file-name`
- `r/restore file-name`: Replace the current queue with a playlist from `file-name`
- `h/help`: Show help message
- `Ctrl-C`: Exit Google Py Music

When playing music:

- `spc`: Play/pause
- `9/0`: Volume down/up (Note: volume changes are not persistent across songs, so I recommend you adjust your system volume instead)
- `n`: Next track
- `q`: Stop
- `↑/↓/←/→`: Seek

## Accounts

Google Py Music works similiarly to the web interface in that users with free accounts can only arbitrarily access music that they've purchased or uploaded, whereas users with free accounts can search for and stream anything. When playing music with a free account, the entire song is downloaded and played locally rather than streamed.

Notes for free users:

- A one-time OAuth sign-in is required for free users, run `gpymusic-oauth-login`  `bin/oauth_login` and follow the prompts to authorize.
- If you don't want to wait for songs to download on the fly, you can download them all in one go with `gpymusic-download-all` or `bin/download_all.py`. Songs are stored in `~/.local/share/gpymusic/songs`.
- The `e/expand` command does not work for free users because artists and albums cannot be generated, so there is nothing for it to do.
- I don't have enough music uploaded to my free account to properly test it, so please [open issues](https://github.com/christopher-dG/gpymusic/issues/new) about any crashes or other problems.

## 2-Factor Authentication

If your account has 2FA set up, you will need to use an [app password](https://support.google.com/accounts/answer/185833?hl=en) to log in. If you're storing your password in your config file, replace it with the app password.

## Crashes

If `gpymusic` crashes, your terminal settings will likely be messed up, in which case `stty sane` will restore order. Don't forget to [open an issue](https://github.com/christopher-dG/gpymusic/issues/new)!

***

Thanks for using Google Py Music!
