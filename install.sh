#!/usr/bin/env bash
echo "Installing pmcli."
mkdir -p ~/.config/pmcli
cp config.example mpv_input.conf ~/.config/pmcli/config
mkdir -p ~/.local/share/pmcli
cp *.py *.sh ~/.local/share/pmcli
chmod +x ~/.local/share/pmcli/pmcli.py
sudo ln -s /home/${USER}/.local/share/pmcli/pmcli.py /usr/local/bin/pmcli

echo "Installed pmcli."