#!/usr/bin/env bash
echo "Installing pmcli."
mkdir -p ~/.config/pmcli
cp config.example ~/.config/pmcli/config
chmod +x ~/.local/share/pmcli/pmcli.py
mkdir -p ~/.local/share/pmcli
cp *.py *.sh ~/.local/share/pmcli
sudo ln -s /home/${USER}/.local/share/pmcli/pmcli.py /usr/local/bin/pmcli
echo "Installed pmcli."