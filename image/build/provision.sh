#!/usr/bin/env bash
# =====================================================================
# abilithic DHC — Provision canonical "dirty state" (v0.1 / 5 check Easy)
# Menanam 5 celah terkontrol. Jalankan di VM base (Ubuntu Server 24.04) sbg root.
# PERINGATAN: hanya untuk VM lomba terisolasi, JANGAN di mesin produksi.
# =====================================================================
set -euo pipefail
if [[ $EUID -ne 0 ]]; then echo "Jalankan sebagai root (sudo)."; exit 1; fi

echo "[1/5] ssh_root_disabled -> set PermitRootLogin yes (rentan)"
if [[ -f /etc/ssh/sshd_config ]]; then
  sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
  grep -q '^PermitRootLogin' /etc/ssh/sshd_config || echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
  systemctl restart ssh || true
fi

echo "[2/5] ufw_enabled -> matikan firewall (rentan)"
apt-get install -y ufw >/dev/null 2>&1 || true
ufw --force disable || true

echo "[3/5] telnet_disabled -> pasang & nyalakan telnetd (rentan)"
apt-get install -y telnetd inetutils-inetd >/dev/null 2>&1 || \
  apt-get install -y telnetd >/dev/null 2>&1 || true
systemctl enable --now inetd 2>/dev/null || systemctl enable --now telnetd 2>/dev/null || true

echo "[4/5] rogue_user_removed -> tambahkan user 'hacker' (rentan)"
if ! id hacker >/dev/null 2>&1; then
  useradd -m -s /bin/bash hacker || true
  echo 'hacker:password123' | chpasswd || true
fi

echo "[5/5] shadow_perm -> longgarkan permission /etc/shadow (rentan)"
chmod 644 /etc/shadow || true

echo "Selesai. Canonical dirty state v0.1 terpasang."
echo "Catat image_version dan hitung baseline hash sebelum export OVA."
