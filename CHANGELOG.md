# Changelog

Semua perubahan penting dicatat di sini. Format: [Keep a Changelog](https://keepachangelog.com),
versi mengikuti [SemVer](https://semver.org) (TDD §24).

## [Unreleased]
### Added
- **Kiosk otomatis membuka lagi kalau jendelanya ditutup**: sebelumnya kalau
  peserta tidak sengaja menutup window (klik close/Alt+F4), `kiosk.py`
  langsung keluar dan peserta kehilangan akses sampai ada yang menjalankan
  ulang manual. Sekarang `main()` (`agent/kiosk.py`) loop selamanya dan
  membuka lagi window otomatis dalam ~2 detik. Sebagai fallback kalau proses
  kiosk-nya sendiri ikut mati, ditambahkan shortcut Desktop **"Restart
  abilithic DHC"** (`agent/kiosk/restart-kiosk.desktop` +
  `restart-kiosk.sh`) yang tinggal di-double-click tanpa buka terminal.
- **Icon abilithic dipakai konsisten di kiosk**: logo placeholder (`◈`) di
  UI kiosk lokal (`agent/ui/templates/index.html`) diganti gambar asli
  (disajikan lewat route static Flask baru, `agent/ui/static/`), dan ikon
  window/taskbar kiosk (`agent/kiosk/abilithic-dhc.desktop`, shortcut
  restart) diarahkan ke ikon yang sama alih-alih ikon generik
  `utilities-terminal`.
- **Panduan troubleshooting VM** ditambahkan di README (ringkas, EN) dan
  `docs/DEPLOYMENT-GUIDE.md` (lengkap, ID): alur run awal, cara update kode
  di VM yang benar (termasuk resync wajib ke `/opt/abilithic-agent/` yang
  sebelumnya sering terlewat), penanganan window kiosk tertutup, dan
  kumpulan command diagnostik umum.
- **Transparansi skor di leaderboard publik**: baris/skor peserta kini bisa
  diklik untuk membuka rincian per-soal (judul + status lulus/belum, plus
  ringkasan "X / Y soal selesai") — sebelumnya leaderboard cuma menampilkan
  nama & angka total. Endpoint baru (publik, read-only, tanpa jawaban/command):
  `GET /api/v1/leaderboard/detail?participant=<id>` (`web/app/api/v1/leaderboard/detail/route.ts`).
  UI: `web/app/page.tsx` (baris expand/collapse), `web/app/globals.css`
  (`.detail-row`, `.detail-grid`, dst.).
- **Hint di kiosk kini klik-untuk-tampil**: sebelumnya hint langsung tampil
  otomatis untuk soal yang belum lulus; sekarang disembunyikan default dan
  baru muncul saat baris soal diklik (klik lagi untuk sembunyikan). Status
  buka/tutup disimpan per soal di sisi klien (`agent/ui/templates/index.html`),
  bertahan walau daftar soal di-render ulang tiap 2 detik.

### Fixed
- **Command perbaikan `empty_password_removed` & `uid0_unique` bisa gagal
  walau sudah "benar" secara logika**, ditemukan setelah dilaporkan pengguna
  mencoba kunci jawaban tapi soal tetap tidak PASS:
  - `uid0_unique`: `sudo userdel rootkit` (tanpa `-f`) ditolak dengan
    `user is currently used by process ...` — false-positive, karena akun
    `rootkit` sengaja berbagi UID 0 dengan `root` (`useradd -o -u 0`), dan
    `userdel` mendeteksi "sedang dipakai" dengan mencocokkan UID, bukan nama
    user; root selalu punya banyak proses berjalan. Fix: **wajib** pakai
    `sudo userdel -f rootkit`.
  - `empty_password_removed`: `sudo passwd -l guest2` bisa tidak konsisten
    mengubah field password di `/etc/shadow` pada akun yang field-nya BENAR-
    BENAR kosong (bukan sekadar terkunci). Diganti rekomendasi utama:
    `sudo usermod -p '!' guest2` — menulis langsung field password ke `!`
    tanpa logika toggle apa pun, hasilnya pasti tidak kosong lagi.
  - Diperbarui di `agent/checks/uid0_unique/manifest.yaml`,
    `agent/checks/empty_password_removed/manifest.yaml`,
    `db/seed/difficulties.sql`, dan kunci jawaban internal panitia.

### Changed
- **Teks 15 soal hardening dibuat lebih profesional**: `title` & `description`
  tiap check (`agent/checks/*/manifest.yaml`, disinkronkan ke
  `db/seed/difficulties.sql`) ditulis ulang jadi kalimat formal lengkap,
  konsisten gaya bahasanya antar-soal (mis. "Nonaktifkan Login Root melalui
  SSH" — sebelumnya "Nonaktifkan SSH root login"). `hint_basic` &
  `hint_advanced` (termasuk command perbaikan) TIDAK dihapus/diubah maknanya
  — beberapa hanya disinkronkan agar identik antara database & agent.

### Fixed
- **Jendela kiosk blank setelah restart VM** (`agent/kiosk.py`), dua penyebab
  sekaligus:
  1. Bug WebKitGTK yang dikenal luas: renderer DMA-BUF-nya sering gagal total
     di GPU virtual (VMware/VirtualBox/QEMU), menghasilkan jendela yang
     terbuka tapi benar-benar blank. Diperbaiki dengan set
     `WEBKIT_DISABLE_DMABUF_RENDERER=1` & `WEBKIT_DISABLE_COMPOSITING_MODE=1`
     sebelum WebKit diinisialisasi.
  2. Race condition: window sebelumnya memuat URL agent sekali saja tanpa
     retry — kalau server Flask belum sempat nyala saat VM baru boot
     (jaringan/servis masih "pemanasan"), window gagal memuat dan terlihat
     kosong selamanya. Diperbaiki: window kini dibuka dengan halaman loading
     lokal instan (tidak butuh server), lalu background thread menunggu UI
     siap (timeout dinaikkan 40s -> 120s) baru mengalihkan window ke URL asli.
     Kalau tetap gagal, tampil halaman error yang jelas (bukan blank).

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
    CONTRIBUTING, CODE_OF_COND