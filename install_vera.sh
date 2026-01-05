#!/bin/bash

echo "🔹 V.E.R.A. DEPLOYMENT PROTOCOL INITIATED 🔹"

# 1. System Updates & Dependencies
echo ">> Updating System Repositories..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv portaudio19-dev libpq-dev git

# 2. Permissions (GPS & Serial)
echo ">> Granting User Hardware Permissions..."
sudo usermod -a -G dialout $USER
sudo usermod -a -G audio $USER

# 3. Python Environment Setup
echo ">> Creating Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo ">> Installing Python Libraries..."
pip install -r requirements.txt

# 4. Piper TTS Setup (ARM64 for Pi 5)
echo ">> Downloading Piper TTS (Voice Module)..."
# Note: User must verify the correct binary for their architecture if not on Pi 5
# This fetches the latest Piper executable logic (simplified for script)
pip install piper-tts 

# 5. Service Configuration
echo ">> Installing Systemd Service..."
SERVICE_FILE="/etc/systemd/system/vera.service"

# Generate the service file dynamically based on current path
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=V.E.R.A. Core System
After=network.target sound.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $(pwd)/vera_web.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# 6. Enable Service
sudo systemctl daemon-reload
sudo systemctl enable vera.service

echo "✅ INSTALLATION COMPLETE."
echo ">> Reboot the Pi to finalize permissions and start V.E.R.A."