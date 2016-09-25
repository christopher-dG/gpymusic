#!/usr/bin/env bash
echo "Uninstalling pmcli."
rm -rf ~/.local/share/pmcli ~/.config/pmcli/
sudo rm /usr/local/bin/pmcli
echo "Uninstalled pmcli."