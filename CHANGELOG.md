# Changelog

Semua perubahan penting dicatat di sini. Format: [Keep a Changelog](https://keepachangelog.com),
versi mengikuti [SemVer](https://semver.org) (TDD §24).

## [Unreleased]
### Changed
- **Branding di web portal**: logo placeholder (`◈`) di leaderboard & admin
  console diganti dengan logo abilithic sungguhan (`web/public/abilithic-icon-256.png`,
  disalin dari `assets/abilithic-icon-256.png`), juga dipakai sebagai favicon
  (`web/app/layout.tsx`). Nama sesi default saat buat lomba baru diubah dari
  "Lomba DHC #1" menjadi "Defense Hardening Competition #1"
  (`web/app/admin/page.tsx`).

### Fixed
- **Soal `telnet_disabled` bisa "PASS sendiri" tanpa peserta berbuat apa-apa**:
  provisioning lama bergantung pada paket `telnetd`/`inetd`, yang sudah tak
  bisa diandalkan (sering gagal terpasang / tak bisa jalan lewat systemd) di
  Ubuntu modern — kalau gagal, tidak pernah ada apa pun yang listen di port
  23, jadi soal ini otomatis lolos sejak awal. Diganti listener TCP minimal
  buatan sendiri, tanpa dependensi paket telnet apa pun: `image/build/dhc-telnetd.py`
  (service) + `image/build/dhc-telnetd.service` (unit systemd), dipasang &
  diaktifkan oleh `provision.sh`. Peserta mematikan dengan
  `sudo systemctl disable --now dhc-telnetd`. Hint di database
  (`db/seed/difficulties.sql`, `agent/checks/telnet_disabled/manifest.yaml`)
  & kunci jawaban internal diperbarui mengikuti.
- **`provision.sh` sekarang dua fase (RESET lalu PLANT)**: sebelum menanam 15
  celah, skrip lebih dulu membersihkan sisa provisioning/percobaan
  sebelumnya — hapus user rogue lama, `ufw --force reset`, lepas mask/disable
  `dhc-telnetd`, dan buang override `net.ipv4.ip_forward` yang mungkin
  ter-persist ke `/etc/sysctl.conf`/`/etc/sysctl.d/` saat peserta melakukan
  fix. Ini membuat provisioning deterministik walau dijalankan berkali-kali
  di VM yang sama (skenario umum saat testing berulang sebelum lomba
  sesungguhnya).
- **Akar masalah "poin/timestamp tidak update otomatis"**: agent kini
  menyinkronkan jam ke server (`GET /api/v1/time`, tanpa signing) sebelum
  setiap siklus, lalu mengoreksi timestamp HMAC-nya dengan offset itu
  (`agent/crypto/signing.py`, `agent/network/client.py`). Sebelumnya, agent
  menandatangani request dengan jam lokal VM mentah; VM hasil clone/template
  VMware yang jamnya meleset >5 menit (jendela toleransi server) membuat
  semua request ditolak diam-diam sampai jam VM dikoreksi manual. Timer
  countdown, `computed_at_ms` skor, dan `taken_at_server_ms` snapshot ikut
  dikoreksi (`agent/main.py`, `agent/snapshot/manager.py`). Lihat
  `docs/REVIEW-AND-CONCEPT-v2.md` §2 untuk diagnosis lengkap. Test regresi:
  `tests/test_clock_skew.py`.
- **Admin console tidak auto-refresh**: daftar sesi & peserta kini polling
  otomatis (5s / 4s) alih-alih menunggu reload manual (`web/app/admin/page.tsx`).

### Added (v0.2 — dalam progres)
- **Web console pro**: login persisten (sesi cookie httpOnly), kelola event
  (hapus/arsip sesi), kelola peserta (daftar, diskualifikasi, hapus), redesain UI
  (branding, badge status, medali, toast, loading/empty state).
- **Agent kiosk**: `kiosk.py` menampilkan agent sebagai aplikasi fullscreen
  (pywebview + fallback browser-kiosk), autostart `.desktop`, `install-kiosk.sh`,
  UI lokal dipoles. Peserta zero-setup: boot VM → app muncul otomatis.

- **15 check** (dari 5): +passwd_perm, empty_password_removed, uid0_unique,
  ip_forward_disabled, password_max_days, ssh_permitempty_disabled,
  world_writable_removed, suid_bash_removed, rogue_sudo_removed, cron_backdoor_removed.
- **Tingkat berbeda nyata**: Easy 6 soal · Medium 11 · Hard 15 (subset di seed).
- **Custom timer** saat buat sesi (menit), default per tingkat.
- **Batalkan diskualifikasi** (requalify) di admin.
- Kiosk jadi **jendela companion** (bukan fullscreen-lock) agar peserta bisa pakai terminal.
- **Indikator koneksi** (titik hijau/kuning/merah) + tombol **"Sinkron sekarang"** di panel
  peserta → paksa agent poll ke server tanpa nunggu interval.
- `run-agent.sh`: jalankan agent bersih (auto-bunuh proses lama di port 8080).

### Changed
- Admin auth pindah dari header password ke sesi cookie (lib/auth.ts).
- `provision.sh` menanam **15 celah**; seed pakai UPSERT (aman dijalankan ulang).
- UI leaderboard/admin/kiosk dipoles: indikator "Live", skeleton loading,
  micro-interaction hover/transisi, highlight juara #1 (`web/app/globals.css`,
  `web/app/page.tsx`, `web/app/admin/page.tsx`, `agent/ui/templates/index.html`).
- README ditulis ulang mengikuti pola abilithic-recon & abilithic-scan
  (badge, hero, screenshots, footer branding); tambah `DISCLAIMER.md` dan
  `assets/README.md`.
- **Port lokal kiosk/agent: `8080` → `9090`** (`agent/config.example.yaml`,
  `agent/kiosk.py`, `agent/main.py`, `agent/ui/server.py`, `agent/run-agent.sh`,
  `README.md`, `docs/setup-participant.md`, `docs/DEPLOYMENT-GUIDE.md`) — 8080
  lazim dipakai proxy Burp Suite/OWASP ZAP di mesin tester, jadi dihindari agar
  agent bisa jalan berdampingan dengan alat itu di komputer yang sama. Entri
  changelog historis di atas (v0.1/v0.2) sengaja tidak diubah.
- **Reorganisasi dokumen untuk presentasi GitHub yang lebih profesional**:
  - `KONSEP-abilithic-defensive-competition.md` (TDD asli, sebelumnya hidup di
    luar repo git dan tak pernah ter-upload) dipindahkan ke dalam repo sebagai
    `docs/TECHNICAL-DESIGN.md`.
  - `REVIEW-DAN-KONSEP-v2.md` (root, nama campur bahasa) → `docs/REVIEW-AND-CONCEPT-v2.md`.
  - `PANDUAN-SETUP-v0.1.md` (root) → `docs/DEPLOYMENT-GUIDE.md`, disunting agar
    tak lagi menyebut "v0.1"/"5 celah" (sudah 15 celah & 3 tingkat sejak v0.2).
  - Root repo kini hanya berisi file governance standar GitHub (README, LICENSE,
    CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, DISCLAIMER, CHANGELOG); seluruh
    dokumen teknis/naratif panjang ada di `docs/`.

## [0.1.0] — 2026-06-30
### Added
- **Database**: schema Postgres (competitions, participants, checks, difficulties,
  participant_checks, scores, snapshots, event_logs, nonces) + view `leaderboard`.
- **Seed**: preset tingkat Easy/Medium/Hard + 5 check Linux dasar
  (ssh_root_disabled, ufw_enabled, telnet_disabled, rogue_user_removed, shadow_perm).
- **Agent (Python)**: arsitektur modular — state_manager, score_engine (pure fn),
  check_runner, network client + retry/backoff + store-and-forward, snapshot manager,
  crypto HMAC signing, logger terstruktur, local UI (localhost:8080).
- **Web (Next.js)**: API `/v1` (register, state, score, heartbeat, snapshot, admin),
  leaderboard realtime (Supabase Realtime), halaman admin START/PAUSE/STOP.
- **Baseline & Evidence**: snapshot registration/start/stop + eligibility anti pre-fix.
- **Governance**: README, LICENSE (MIT), CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, ADR-001..006.
- **CI**: GitHub Actions (lint + unit test scoring).

[Unreleased]: https://github.com/abilithic/abilithic-defensive-competition/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/abilithic/abilithic-defensive-competition/releases/tag/v0.1.0
