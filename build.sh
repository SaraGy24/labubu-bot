#!/usr/bin/env bash
# Telepítjük a Google Chrome-ot headless módban való futtatáshoz

echo "Installing Google Chrome..."
apt-get update
apt-get install -y wget gnupg2
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get update
apt-get install -y google-chrome-stable
echo "Google Chrome installed!"
