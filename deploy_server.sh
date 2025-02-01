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
netlify deploy --prod --site eda7ac4f-8190-42f1-8de9-33fdb1a09c22

echo "Verification URL: http://your-server-ip"