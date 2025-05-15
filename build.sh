#!/usr/bin/env bash
# Telepítjük a Chromiumot headless módban való futtatáshoz

echo "Installing Chromium..."
apt-get update
apt-get install -y chromium-browser
echo "Chromium installed!"

