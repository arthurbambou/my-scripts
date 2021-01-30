#!/bin/bash

sudo apt update
sudo apt list --upgradable
sudo apt upgrade

flatpak update

python3 <(curl -s https://raw.githubusercontent.com/arthurbambou/my-scripts/main/update-not-ppa-deb.py) update