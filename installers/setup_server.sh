#!/bin/bash
TARGET_DIR="$HOME/public_html/ia-player"

# Clean existing installation if not a valid git repo
if [ -d "$TARGET_DIR" ]; then
    if [ -d "$TARGET_DIR/.git" ]; then
        echo "Found existing repository - updating..."
        cd "$TARGET_DIR"
        git reset --hard HEAD
        git clean -fd
        git pull origin main
    else
        echo "WARNING: Non-Git files detected in $TARGET_DIR"
        echo "Creating backup and cleaning directory..."
        mv "$TARGET_DIR" "$TARGET_DIR.bak-$(date +%s)"
        mkdir -p "$TARGET_DIR"
    fi
else
    mkdir -p "$TARGET_DIR"
fi

# Fresh clone if directory is empty
cd "$TARGET_DIR"
if [ -z "$(ls -A .)" ]; then
    git clone https://github.com/robklaiss/ia-player.git .
else
    echo "Existing files detected after cleanup. Aborting."
    exit 1
fi

# Final setup steps
chmod +x installers/server/*.sh
./installers/server/install_dependencies.sh
./installers/server/setup_venv.sh
echo "Server setup complete. Activate with: source .venv/bin/activate"