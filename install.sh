#!/bin/bash
set -e

# Install
echo "Installing pmcli."
mkdir -p ~/.config/pmcli ~/.local/share/pmcli/playlists
cp config.example.json mpv_input.conf ~/.config/pmcli
cp ~/.config/pmcli/config.example.json ~/.config/pmcli/config.json
cp -r src ~/.local/share/pmcli
sudo ln -s ~/.local/share/pmcli/src/pmcli.py /usr/local/bin/pmcli

echo "Done: don't forget to edit ~/.config/pmcli/config.json."
