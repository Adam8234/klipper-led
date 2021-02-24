#!/usr/bin/env bash
PYTHONDIR="${HOME}/klipperled-env"
SYSTEMDDIR="/etc/systemd/system"
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Use Klippers env
[ ! -d ${PYTHONDIR} ] && virtualenv -p python3 ${PYTHONDIR}

sudo /bin/sh -c "cat > $SYSTEMDDIR/klipperled.service" << EOF
#Systemd service file for klipper
[Unit]
Description=Starts klipperled on startup
After=network.target
[Install]
WantedBy=multi-user.target
[Service]
Type=simple
User=root
RemainAfterExit=yes
ExecStart=${PYTHONDIR}/bin/python ${SRCDIR}/app.py
Restart=always
RestartSec=10
EOF
sudo systemctl enable klipperled
sudo systemctl start klipperled