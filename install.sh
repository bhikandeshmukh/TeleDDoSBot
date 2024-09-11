#!/bin/bash

# Update and install dependencies for Kali Linux
if [[ -n "$(command -v apt)" ]]; then
    echo "Installing dependencies on Kali Linux..."
    sudo apt update
    sudo apt install -y python3 python3-pip
    pip3 install -r requirements.txt

# Update and install dependencies for Termux
elif [[ -n "$(command -v pkg)" ]]; then
    echo "Installing dependencies on Termux..."
    pkg update
    pkg upgrade
    pkg install -y python
    pip install -r requirements.txt

else
    echo "Unsupported environment. Please install dependencies manually."
fi