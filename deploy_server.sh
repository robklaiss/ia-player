#!/bin/bash
# Server deployment script
set -e

SERVER_USER="coati23"
PI_USER="infoactive"

echo "=== Starting Server Deployment ==="

# Push latest changes
git push origin main

echo "=== Deploying to Netlify ==="
npm install -g netlify-cli
netlify deploy --prod

echo "Verification URL: http://your-server-ip"