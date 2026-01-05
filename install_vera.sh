#!/bin/bash

# V.E.R.A. Deployment Protocol V1.1
# Targeted for Raspberry Pi OS (Bookworm/Bullseye)

set -e  # Exit immediately if a command fails

echo "🔹 V.E.R.A. DEPLOYMENT PROTOCOL INITIATED 🔹"

# 1. System Updates & Hard Dependencies
echo ">> Updating System Repositories..."
sudo apt update && sudo apt upgrade -y

echo ">> Installing Audio & Math Dependencies (Crucial for ARM)..."
# added espeak-ng (for TTS) and libatlas (for NumPy/AI math)
sudo apt install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    libpq-dev \
    git \
    espeak-ng \
    libatlas-base-dev 

# 2. Permissions (GPS & Serial)
echo ">> Granting User Hardware Permissions..."
# Added 'gpio' just in case you use sensors later
sudo usermod -a -G dialout,audio,gpio,video $USER

# 3. Python Environment Setup
echo ">> Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo ">> Installing Python Libraries..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Piper TTS Check
# We rely on requirements.txt, but explicit check ensures binary exists
if ! pip show piper-tts > /dev/null; then
    echo ">> Installing Piper TTS..."
    pip install piper-tts
fi

# 5. Service Configuration
echo ">> Installing Systemd Service..."
SERVICE_FILE="/etc/systemd/system/vera.service"
CURRENT_DIR=$(pwd)

# Generate the service file
# Note: Changed to network-online.target for safety
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=V.E.R.A. Core System
After=network-online.target sound.target
Wants=network-online.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/vera_web.py
Environment="PATH=$CURRENT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# 6. Enable Service
sudo systemctl daemon-reload
sudo systemctl enable vera.service

echo "✅ INSTALLATION COMPLETE."
echo ">> Please REBOOT to finalize group permissions."