#!/bin/bash
echo "Configuring player..."
# Add hardware-specific configuration here
sudo raspi-config nonint do_memory_split 256
sudo apt-get install -y libmpv-dev
