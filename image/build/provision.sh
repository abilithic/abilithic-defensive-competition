#!/usr/bin/env bash
# =====================================================================
# abilithic DHC — Provision canonical "dirty state" (v0.2 / 15 celah)
# Menanam SEMUA celah. Tingkat kesulitan (dipilih di web) menentukan
# subset mana yang dinilai — jadi tanam semua di sini.
# Jalankan di VM base sbg root.  PERINGATAN: hanya untuk VM lomba terisolasi.
# =====================================================================
set -uo pipefail
if [[ $EUID -ne 0 ]]; then echo "Jalankan sebagai root (sudo)."; exit 1; fi
echo "== Menanam 15 celah abilithic DHC =="

# 1 ssh_root_disabled -> PermitRootLogin yes
if [[ -f /etc/ssh/sshd_config ]]; then
  sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
  grep -q '^PermitRootLogin' /etc/ssh/sshd_config || echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
fi

# 11 ssh_permitempty_disabled -> PermitEmptyPasswords yes
if [[ -f /etc/ssh/sshd_config ]]; then
  sed -i 's/^#\?PermitEmptyPasswords.*/PermitEmptyPasswords yes/' /etc/ssh/sshd_config
  grep -q '^PermitEmptyPasswords' /etc/ssh/sshd_config || echo 'PermitEmptyPasswords yes' >> /etc/ssh/sshd_config
  systemctl restart ssh 2>/dev/null || true
fi

# 2 ufw_enabled -> matikan firewall
apt-get install -y ufw >/dev/null 2>&1 || true
ufw --force disable >/dev/null 2>&1 || true

# 3 telnet_disabled -> pasang telnetd (best-effort; mungkin gagal di 26.04)
apt-get install -y telnetd >/dev/null 2>&1 || apt-get install -y inetutils-telnetd >/dev/null 2>&1 || true
systemctl enable --now inetd 2>/dev/null || systemctl enable --now telnetd 2>/dev/null || true

# 4 rogue_user_removed -> user 'hacker'
id hacker >/dev/null 2>&1 || { useradd -m -s /bin/bash hacker 2>/dev/null || true; echo 'hacker:password123' | chpasswd 2>/dev/null || true; }

# 5 shadow_perm -> longgarkan
chmod 644 /etc/shadow 2>/dev/null || true

# 6 passwd_perm -> world-writable
chmod 666 /etc/passwd 2>/dev/null || true

# 7 empty_password_removed -> akun password kosong
id guest2 >/dev/null 2>&1 || useradd -m -s /bin/bash guest2 2>/dev/null || true
passwd -d guest2 >/dev/null 2>&1 || true

# 8 uid0_unique -> akun UID 0 palsu
id rootkit >/dev/null 2>&1 || useradd -o -u 0 -M -s /bin/bash rootkit 2>/dev/null || true

# 9 ip_forward_disabled -> nyalakan
sysctl -w net.ipv4.ip_forward=1 >/dev/null 2>&1 || true

# 10 password_max_days -> set 99999
if grep -q '^PASS_MAX_DAYS' /etc/login.defs; then
  sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS\t99999/' /etc/login.defs
else
  echo 'PASS_MAX_DAYS	99999' >> /etc/login.defs
fi

# 12 world_writable_removed -> file sentinel 777
mkdir -p /opt/dhc; echo "rahasia" > /opt/dhc/secret.txt; chmod 777 /opt/dhc/secret.txt

# 13 suid_bash_removed -> backdoor SUID
cp /bin/bash /usr/local/bin/rootbash 2>/dev/null && chmod 4755 /usr/local/bin/rootbash 2>/dev/null || true

# 14 rogue_sudo_removed -> user 'backdoor' di grup sudo
id backdoor >/dev/null 2>&1 || useradd -m -s /bin/bash backdoor 2>/dev/null || true
usermod -aG sudo backdoor 2>/dev/null || true

# 15 cron_backdoor_removed -> cron mencurigakan
cat > /etc/cron.d/dhc-backdoor <<'EOF'
* * * * * root /bin/true
EOF

echo "== Selesai. 15 celah tertanam (sebagian telnet bisa gagal di 26.04 — normal). =="
echo "   Catat image_version & hitung baseline hash sebelum export OVA."
