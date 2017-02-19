#!/bin/bash
set -e

# Backup
echo "Backing up configs."
mkdir ~/.config/pmcli-backup
cp ~/.config/pmcli/*.json ~/.config/pmcli-backup

# Uninstall
echo "Uninstalling pmcli."
rm -r ~/.local/share/pmcli ~/.config/pmcli
sudo rm /usr/local/bin/pmcli

# Install
echo "Reinstalling pmcli."
mkdir -p ~/.config/pmcli ~/.local/share/pmcli/playlists
cp config.example.json mpv_input.conf ~/.config/pmcli
cp ~/.config/pmcli/config.example.json ~/.config/pmcli/config.json
cp -r src ~/.local/share/pmcli
sudo ln -s ~/.local/share/pmcli/src/pmcli.py /usr/local/bin/pmcli

# Restore
echo "Restoring configs."
mv ~/.config/pmcli-backup/* ~/.config/pmcli
rmdir ~/.config/pmcli-backup

echo "Done."
