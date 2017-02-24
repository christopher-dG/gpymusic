#!/bin/bash
set -e

echo Updating pmcli.
cd ..
git pull origin master
rm -r ~/.local/share/pmcli/src
cp -r src ~/.local/share/pmcli
cd script
echo Done.
