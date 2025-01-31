#!/bin/bash
# Server initialization script
mkdir -p ~/ia-player && cd ~/ia-player
git clone https://github.com/robklaiss/ia-player.git . || exit 1

chmod +x installers/server/*.sh
./installers/server/install_dependencies.sh && \
./installers/server/setup_venv.sh && \
echo "Server setup complete. Activate with: source .venv/bin/activate"
