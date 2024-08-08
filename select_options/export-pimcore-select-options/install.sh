#!/bin/sh

set -e

# For Debian-based systems

if [ -f /etc/debian_version ]; then
    sudo apt-get install -y python3-pymysql python3-odf
else
    echo "This script is only for Debian-based systems"
    exit 1
fi
