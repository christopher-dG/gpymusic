#!/usr/bin/env bash
echo "Installing pmcli."
mkdir /home/${SUDO_USER}/.config/pmcli /etc/pmcli
cp config mpv_input.conf /home/${SUDO_USER}/.config/pmcli
cp -r pmcli install.sh uninstall.sh /etc/pmcli
ln -s /etc/pmcli/pmcli/pmcli.py /usr/local/bin/pmcli
mkdir -p /home/${SUDO_USER}/.local/share/applications
cp pmcli.desktop /home/${SUDO_USER}/.local/share/applications
chown -R ${SUDO_USER} /home/${SUDO_USER}/.config/pmcli /home/${SUDO_USER}/.local/share/applications/pmcli.desktop
chmod +x /etc/pmcli/pmcli/pmcli.py /home/${SUDO_USER}/.local/share/applications/pmcli.desktop
