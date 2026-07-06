#!/usr/bin/env bash
# =====================================================================
# abilithic DHC — Restart manual kiosk (fallback kalau window macet/hilang
# dan auto-relaunch di kiosk.py sendiri entah kenapa tidak jalan).
# Dipanggil oleh shortcut Desktop "Restart abilithic DHC.desktop", atau
# jalankan langsung: bash /opt/abilithic-agent/kiosk/restart-kiosk.sh
# =====================================================================
set -uo pipefail

LOG="/tmp/abilithic-kiosk.log"

echo "[restart-kiosk] menghentikan instance kiosk.py lama (kalau ada)..." >> "$LOG"
pkill -f "python3 .*kiosk.py" 2>/dev/null || true
sleep 1

echo "[restart-kiosk] membuka kiosk.py baru..." >> "$LOG"
nohup /usr/bin/python3 /opt/abilithic-agent/kiosk.py >> "$LOG" 2>&1 &
disown

exit 0
