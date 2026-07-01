#!/usr/bin/env bash
# =====================================================================
# abilithic DHC — Jalankan agent dengan BERSIH.
# Otomatis membunuh proses lama yang memegang port 8080 (biang "Address
# already in use" / dashboard tak update), lalu menjalankan agent baru.
# Pakai:  sudo bash agent/run-agent.sh     (atau dari /opt: sudo bash /opt/abilithic-agent/run-agent.sh)
# =====================================================================
set -u
PORT=8080

PIDS=$(lsof -t -i:"$PORT" 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  echo "[run-agent] menutup proses lama di :$PORT -> $PIDS"
  kill -9 $PIDS 2>/dev/null || true
  sleep 1
fi
pkill -9 -f kiosk.py 2>/dev/null || true

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[run-agent] menjalankan agent dari $DIR"
exec python3 "$DIR/main.py" 2>&1 | tee /tmp/agent.log
