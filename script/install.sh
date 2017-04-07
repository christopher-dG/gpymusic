#!/bin/bash
set -e

[ $USER = root ] && echo "Don't run this script as root." && exit 1
DIR=$(dirname $(dirname $(realpath $BASH_SOURCE)))

echo "Installing Google Py Music."
mkdir -p ~/.local/share/gpymusic/{playlists,songs}
cp -r $DIR/config ~/.config/gpymusic
cp ~/.config/gpymusic/config.example.json ~/.config/gpymusic/config.json
cp -r $DIR/src ~/.local/share/gpymusic
sudo ln -s ~/.local/share/gpymusic/src/main.py /usr/local/bin/gpymusic

echo "Done: don't forget to edit ~/.config/gpymusic/config.json."
