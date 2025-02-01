#!/bin/bash
# Server deployment script
set -e

echo "=== Starting Server Deployment ==="

# Push latest changes
git push origin main

# Execute deployment commands
ssh -tt coati23@vinculo.com.py << 'EOSSH'
cd ~/public_html/ia-player
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
systemctl --user restart ia-player.service
nohup ./caddy start > caddy.log 2>&1 &
echo "Deployment completed successfully!"
exit 0
EOSSH

echo "Verification URL: http://your-server-ip"