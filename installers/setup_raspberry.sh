#!/bin/bash
TARGET_DIR="$HOME/ia-player"

# Create target directory if needed
mkdir -p "$TARGET_DIR" && cd "$TARGET_DIR" || exit 1

# Check if directory contains git repo
if [ -d ".git" ]; then
    echo "Updating existing Pi installation..."
    git pull origin main
else
    if [ "$(ls -A .)" ]; then
        echo "ERROR: Directory $TARGET_DIR contains non-Git files. Please:"
        echo "1. Backup/remove existing files"
        echo "2. Run this script again"
        exit 1
    else
        git clone https://github.com/robklaiss/ia-player.git .
    fi
fi

# Continue with setup
sudo chmod +x installers/raspberry/*.sh
sudo ./installers/raspberry/configure_player.sh
sudo ./installers/raspberry/deploy_player.sh
echo "Player service active. Check status: sudo systemctl status ia-player.service"