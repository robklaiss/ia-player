#!/bin/bash
git push origin main && \
ssh coati23@vinculo.com.py "cd ~/public_html/ia-player && git pull && ./installers/setup_server.sh" && \
ssh infoactive@raspberrypi "cd ~/ia-player && git pull && sudo ./installers/setup_raspberry.sh"