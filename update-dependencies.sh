#!/bin/bash

echo "======APT Updates======"
sudo apt update
sudo apt list --upgradable
sudo apt upgrade

echo "====Flatpak Updates===="
flatpak update

echo "=====Other Updates====="
python3 <(curl -s https://raw.githubusercontent.com/arthurbambou/my-scripts/main/update-not-ppa-deb.py) update

echo "==========Done========="