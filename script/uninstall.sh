#!/bin/bash
set -e

$USER -eq root && echo "Don't run this script as root." && exit 1
echo "Uninstalling Google Py Music."
rm -r ~/.local/share/gpymusic ~/.config/gpymusic
sudo rm /usr/local/bin/gpymusic
echo "Done."
