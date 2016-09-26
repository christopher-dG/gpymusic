#!/usr/bin/env bash
echo "Installing pmcli."
mkdir /home/${SUDO_USER}/.config/pmcli /etc/pmcli
cp config mpv_input.conf /home/${SUDO_USER}/.config/pmcli
cp -r pmcli install.sh uninstall.sh /etc/pmcli
chmod +x /etc/pmcli/pmcli/pmcli.py
ln -s /etc/pmcli/pmcli/pmcli.py /usr/local/bin/pmcli
chown -R ${SUDO_USER} /home/${SUDO_USER}/.config/pmcli