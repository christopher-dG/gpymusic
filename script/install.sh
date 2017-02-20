#!/bin/bash
set -e

echo Installing pmcli.
cd ..
mkdir -p ~/.config/pmcli ~/.local/share/pmcli/playlists
cp config/* ~/.config/pmcli
cp ~/.config/pmcli/config.example.json ~/.config/pmcli/config.json
cp -r src ~/.local/share/pmcli
sudo ln -s ~/.local/share/pmcli/src/pmcli.py /usr/local/bin/pmcli
cd script
echo Done: don\'t forget to edit \~/.config/pmcli/config.json.
