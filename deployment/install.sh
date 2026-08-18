#!/bin/bash

set -e


APP_DIR="/opt/tgaccessbot"
SERVICE_DIR="/etc/systemd/system"


echo "Installing TG Access Bot"


cp deployment/systemd/*.service $SERVICE_DIR/


systemctl daemon-reload


systemctl enable tgaccess-api
systemctl enable tgaccess-bot
systemctl enable tgaccess-firewall-sync


systemctl restart tgaccess-api
systemctl restart tgaccess-bot


systemctl start tgaccess-firewall-sync


echo "Installation completed"
