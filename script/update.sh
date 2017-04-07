#!/bin/bash
set -e

$USER -eq root && echo "Don't run this script as root." && exit 1
DIR=$(dirname $(dirname $BASH_SOURCE))

echo "Updating Google Py Music."
git pull origin master
rm -r ~/.local/share/gpymusic/src
cp -r $DIR/src ~/.local/share/gpymusic
echo "Done."
