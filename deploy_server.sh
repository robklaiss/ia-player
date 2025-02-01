#!/bin/bash
# Server deployment script
set -e

SERVER_USER="coati23"
PI_USER="infoactive"

echo "=== Starting Server Deployment ==="

echo "=== Handling Local Changes ==="
git stash
git pull origin main || { echo "Pull failed"; exit 1; }
git stash pop || true

echo "=== Updating Raspberry Pi ==="
ssh infoactive@192.168.0.17 "cd ~/ia-player && git pull origin main && source .venv/bin/activate && pip install -r requirements.txt && sudo systemctl restart ia-player.service"

echo "=== Deploying to Netlify ==="
npm install -g netlify-cli
netlify deploy --prod --site eda7ac4f-8190-42f1-8de9-33fdb1a09c22

echo "=== Cleanup ==="
git clean -fd

echo "Verification URL: http://your-server-ip"