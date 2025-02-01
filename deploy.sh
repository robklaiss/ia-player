#!/bin/bash
cd ~/ia-player
rm -rf .git
git clone https://github.com/yourusername/ia-player.git .
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ia-player.service
