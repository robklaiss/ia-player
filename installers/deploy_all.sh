#!/bin/bash
git push origin main && \
ssh coati23@vinculo.com.py "cd ~/public_html/ia-player && git pull && ./installers/setup_server.sh" && \
ssh infoactive@raspberrypi "cd ~/ia-player && git pull && sudo ./installers/setup_raspberry.sh" && \
# Raspberry Pi deployment
ssh pi@raspberrypi.local "cd ~/ia-player && \
    sudo systemctl restart ia-player.service && \
    echo 'Service status:' && \
    sudo systemctl status ia-player.service --no-pager"# 1. Connect to server
    ssh coati23@vinculo.com.py
    
    # 2. Prepare environment
    mkdir -p ~/public_html/ia-player
    cd ~/public_html/ia-player
    
    # 3. Clone repository
    git clone https://github.com/robklaiss/ia-player.git .
    
    # 4. Create virtual environment
    python3 -m venv .venv
    source .venv/bin/activate
    
    # 5. Install dependencies
    pip install -r requirements.txt
    
    # 6. Configure Gunicorn service
    echo "[Unit]
    Description=IA Player Web Application
    After=network.target
    
    [Service]
    User=coati23
    Group=www-data
    WorkingDirectory=/home/coati23/public_html/ia-player
    Environment=\"PATH=/home/coati23/public_html/ia-player/.venv/bin\"
    ExecStart=/home/coati23/public_html/ia-player/.venv/bin/gunicorn --workers 3 --bind unix:ia-player.sock -m 007 wsgi:app
    
    [Install]
    WantedBy=multi-user.target" | sudo tee /etc/systemd/system/ia-player.service
    
    # 7. Configure Nginx
    echo "server {
        listen 80;
        server_name your-domain.com;
    
        location / {
            include proxy_params;
            proxy_pass http://unix:/home/coati23/public_html/ia-player/ia-player.sock;
        }
    }" | sudo tee /etc/nginx/sites-available/ia-player
    
    # 8. Enable configurations
    sudo ln -s /etc/nginx/sites-available/ia-player /etc/nginx/sites-enabled/
    sudo systemctl daemon-reload
    sudo systemctl start ia-player.service
    sudo systemctl enable ia-player.service
    sudo systemctl restart nginx
    
    # 9. Verify installation
    curl localhost