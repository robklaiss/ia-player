#!/bin/bash
echo "Deploying service..."
sudo cp installers/raspberry/ia-player.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ia-player.service
