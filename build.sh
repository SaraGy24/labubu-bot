#!/usr/bin/env bash

echo "Installing Chromium and Chromedriver..."
apt-get update
apt-get install -y chromium chromium-driver
echo "Chromium and Chromedriver installed!"
which chromium
which chromedriver
