#!/bin/bash
set -e

SERVICE_NAME="clevo-animate"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTERVAL=200
DEV=""

if [[ $EUID -ne 0 ]]; then
    echo "Voer uit als root: sudo bash install.sh [--interval ms] [--dev /dev/hidrawN]"
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --interval) INTERVAL="$2"; shift 2 ;;
        --dev)      DEV="$2";      shift 2 ;;
        *) echo "Onbekende optie: $1"; exit 1 ;;
    esac
done

EXEC_ARGS="/usr/bin/python3 ${SCRIPT_DIR}/clevo_animate.py --interval ${INTERVAL}"
[[ -n "$DEV" ]] && EXEC_ARGS="${EXEC_ARGS} --dev ${DEV}"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Clevo keyboard animation daemon
After=multi-user.target

[Service]
Type=simple
ExecStart=${EXEC_ARGS}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo "Service '${SERVICE_NAME}' geïnstalleerd en gestart (interval: ${INTERVAL}ms)."
echo ""
echo "  Status:   systemctl status ${SERVICE_NAME}"
echo "  Logs:     journalctl -u ${SERVICE_NAME} -f"
echo "  Stoppen:  systemctl stop ${SERVICE_NAME}"
