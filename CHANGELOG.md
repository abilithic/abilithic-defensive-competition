# Changelog

Semua perubahan penting dicatat di sini. Format: [Keep a Changelog](https://keepachangelog.com),
versi mengikuti [SemVer](https://semver.org) (TDD §24).

## [Unreleased]
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
