#!/usr/bin/env bash
PYTHONDIR="${HOME}/klippy-env"
SYSTEMDDIR="/etc/systemd/system"

# Use Klippers env
[ ! -d ${PYTHONDIR} ] && virtualenv -p python2 ${PYTHONDIR}

sudo /bin/sh -c "cat > $SYSTEMDDIR/klipp2rrf.service" << EOF
#Systemd service file for klipper
[Unit]
Description=Starts klipp2rrf on startup
After=network.target
[Install]
WantedBy=multi-user.target
[Service]
Type=simple
User=$USER
RemainAfterExit=yes
ExecStart=${PYTHONDIR}/bin/python app.py
Restart=always
RestartSec=10
EOF
sudo systemctl enable klipp2rrf
sudo systemctl start klipp2rrf
