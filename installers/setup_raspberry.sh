#!/bin/bash
# Raspberry Pi initialization script
mkdir -p ~/ia-player && cd ~/ia-player
git clone https://github.com/robklaiss/ia-player.git . || exit 1

sudo chmod +x installers/raspberry/*.sh
sudo ./installers/raspberry/configure_player.sh && \
sudo ./installers/raspberry/deploy_player.sh && \
echo "Player service active. Check status: sudo systemctl status ia-player.service"
