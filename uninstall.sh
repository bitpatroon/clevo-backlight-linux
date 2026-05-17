#!/bin/bash
set -e

SERVICE_NAME="clevo-animate"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ $EUID -ne 0 ]]; then
    echo "Voer uit als root: sudo bash uninstall.sh"
    exit 1
fi

systemctl stop    "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true
rm -f "$SERVICE_FILE"
systemctl daemon-reload

echo "Service '${SERVICE_NAME}' verwijderd."
