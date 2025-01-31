#!/bin/bash
# Read configuration
source setup.conf

# System update
echo "Updating system packages..."
sudo apt update && sudo apt full-upgrade -y

# Install dependencies
echo "Installing required packages..."
sudo apt install -y mpv python3 python3-pip rsync
pip3 install requests flask python-dotenv

# Configure directories
echo "Creating video storage at $video_storage..."
sudo mkdir -p "$video_storage"
sudo chown -R pi:pi "$video_storage"
sudo chmod 775 "$video_storage"

# Configure MPV
echo "Configuring MPV..."
mkdir -p ~/.config/mpv
echo "hwdec=$hwdec" >> ~/.config/mpv/mpv.conf
echo "vo=$vo" >> ~/.config/mpv/mpv.conf

# Deploy services
echo "Configuring system services..."
sudo cp video-sync.service /etc/systemd/system/
sudo cp mpv-player.service /etc/systemd/system/

# Enable services
echo "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable video-sync.service
sudo systemctl enable mpv-player.service

echo "Setup complete! Reboot to start services."