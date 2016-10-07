#!/usr/bin/env bash
echo "Uninstalling pmcli."
rm -rf /home/${SUDO_USER}/.config/pmcli /home/${SUDO_USER}/.local/share/applications/pmcli.desktop /etc/pmcli /usr/local/bin/pmcli
