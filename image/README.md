# Image VM — abilithic DHC

> **OVA tidak disimpan di repo** (terlalu besar). Repo hanya menyimpan **script pembangun**.
> Link unduh OVA + checksum diumumkan di GitHub Releases / Google Drive.

## Cara membangun base image (ringkas)

1. Install **Ubuntu Server 24.04 LTS** di VMware (lihat TDD). Update penuh:
   ```bash
   sudo apt update && sudo apt -y upgrade
   ```
2. **Snapshot "clean baseline"** di VMware (titik balik aman).
3. Pasang agen:
   ```bash
   sudo mkdir -p /opt/abilithic-agent
   sudo cp -r agent/* /opt/abilithic-agent/
   cd /opt/abilithic-agent && sudo cp config.example.yaml config.yaml
   # edit config.yaml -> portal_url ke URL produksi
   sudo apt -y install python3-pip && sudo pip3 install -r requirements.txt
   sudo cp systemd/abilithic-agent.service /etc/systemd/system/
   sudo systemctl daemon-reload && sudo systemctl enable --now abilithic-agent
   ```
4. **Tanam celah (canonical dirty state)** menggunakan `image/build/provision.sh`
   sesuai daftar 5 check v0.1.
5. Catat `image_version` & hitung `canonical_baseline_hash`.
6. **Export OVA**: `File → Export to OVF/OVA`. Hitung checksum:
   ```bash
   sha256sum abilithic-dhc-2024.04.ova
   ```
7. Unggah OVA + checksum ke Releases. Bagikan link ke peserta.

## Daftar celah v0.1 (5 check Easy)

| code | Kondisi rentan (yang ditanam) |
|---|---|
| ssh_root_disabled | `PermitRootLogin yes` di sshd_config |
| ufw_enabled | UFW inactive |
| telnet_disabled | telnetd terpasang & listen di port 23 |
| rogue_user_removed | user `hacker` ditambahkan |
| shadow_perm | `/etc/shadow` di-chmod 644 |

Lihat `image/build/provision.sh`.
