# Review & Concept v2 — abilithic DHC

Review menyeluruh (hulu ke hilir) atas kondisi platform per 2026-07-06, akar
masalah bug "poin/timestamp tidak update otomatis", dan konsep v0.3 untuk
menyempurnakan seluruh aspek: agent, web, database, keamanan, UI/UX, dan
presentasi GitHub. Dokumen ini melengkapi (bukan menggantikan)
[`TECHNICAL-DESIGN.md`](TECHNICAL-DESIGN.md)
(TDD asli) — anggap ini sebagai lapisan "apa yang sudah berjalan, apa yang
bolong, dan apa langkah berikutnya".

**Status singkat**: arsitektur dasarnya sudah solid — modular, ada TDD, ADR,
CI, unit test scoring, baseline/evidence anti pre-fix, store-and-forward,
HMAC signing. Ini BUKAN proyek amatir. Masalah yang ditemukan lebih ke soal
robustness (jam VM), auto-refresh yang belum menyeluruh, dan presentasi
(README/branding) yang belum sejajar dengan abilithic-recon & abilithic-scan.
Bagian di bawah ini rinci per lapisan.

---

## 1. Ringkasan Temuan

| # | Temuan | Dampak | Status |
|---|---|---|---|
| 1 | Agent menandatangani request pakai jam lokal VM, tanpa toleransi clock-skew | Skor/poin "macet" sampai jam VM dikoreksi manual (VMware/Ubuntu) | **Diperbaiki** (§2.1) |
| 2 | Admin console tidak auto-refresh peserta/sesi | Panitia tak lihat status online/offline live tanpa reload manual | **Diperbaiki** (§2.2) |
| 3 | Anti-replay (`nonces` table) ada di schema tapi tidak pernah dipakai | Request ber-signing valid bisa di-*replay* dalam jendela 5 menit | Belum — direkomendasikan v0.3 (§4.4) |
| 4 | Tidak ada rate limiting di `/api/v1/admin/login` | Rentan brute-force password admin | Belum — direkomendasikan v0.3 (§4.4) |
| 5 | Tidak ada NTP/time-sync di provisioning VM | Jam VM hasil clone tetap bisa ngaco di lapisan OS (mitigasi aplikasi sudah ada di #1, ini lapisan pertahanan kedua) | Direkomendasikan v0.3 (§4.5) |
| 6 | UI leaderboard/admin/kiosk sudah modern (dark glassmorphism) tapi minim micro-interaction, skeleton loading, dan indikator "live" | Terasa statis walau datanya sebenarnya sudah live-poll | **Dipoles** (§3) |
| 7 | README & presentasi GitHub tidak sejajar dengan abilithic-recon/abilithic-scan (tanpa badge, logo, screenshot, footer branding) | Kesan proyek kurang matang dibanding proyek Abilithic lain | **Disamakan** (§5) |
| 8 | Tidak bilingual (ID/EN) seperti abilithic-recon & abilithic-scan | Audiens internasional tak terlayani | Direkomendasikan v0.3 (§4.6) |
| 9 | Tidak ada export hasil lomba (CSV/PDF) dari admin console | Panitia harus query manual ke Supabase utk laporan akhir | Direkomendasikan v0.3 (§4.3) |
| 10 | `computed_at_ms` & `taken_at_server_ms` sebelumnya memakai jam lokal VM (bukan cuma header signing) | Ranking tie-break & bukti forensik ikut salah bila jam VM ngaco | **Diperbaiki** (§2.1) |
| 11 | Port lokal kiosk/agent default `8080` bentrok dengan proxy Burp Suite/OWASP ZAP di mesin tester | Tak bisa jalankan agent & Burp bersamaan di komputer yang sama | **Diperbaiki** (§6) |
| 12 | File TDD asli (`KONSEP-abilithic-defensive-competition.md`) hidup di luar repo git, tak pernah ter-upload ke GitHub, dan README lama linknya patah (`../...`) | Dokumen desain utama tidak terlihat/hilang di GitHub | **Diperbaiki** (§6) |

---

## 2. Akar Masalah: "Poin/Timestamp Tidak Update Otomatis"

### 2.1 Diagnosis

Ini bug utama yang dilaporkan. Alurnya:

1. Setiap request agen→server yang sensitif (`/api/v1/state`, `/score`,
   `/heartbeat`, `/snapshot`) wajib HMAC-signed (`agent/crypto/signing.py` →
   `web/lib/hmac.ts`).
2. Signature mencakup `X-Timestamp`, dan server **menolak** request bila
   `|jam_server - X-Timestamp| > 5 menit` (`web/lib/hmac.ts`, `TS_WINDOW_MS`).
3. `X-Timestamp` sebelumnya diambil murni dari `time.time()` lokal di dalam VM
   peserta (`agent/crypto/signing.py`, sebelum perbaikan).
4. **Tidak ada NTP/time-sync apa pun** di `image/build/provision.sh` atau di
   mana pun dalam repo (dicek: tidak ada `ntp`, `chrony`, `timesyncd`,
   `hwclock` sama sekali). VM lomba dijalankan dari image dasar yang di-*clone*
   per peserta (komentar di `provision.sh`: "hanya untuk VM lomba terisolasi")
   — jaringan terisolasi berarti NTP publik pun kemungkinan tidak bisa diakses.
5. Clone/snapshot VMware yang jamnya *frozen* dari saat image dibuat (masalah
   umum & terdokumentasi luas untuk VM template) akan mendorong jam VM di luar
   jendela toleransi 5 menit itu **tanpa peserta sadar**.
6. Begitu itu terjadi: `ApiClient.get_state()` menerima 401 "timestamp out of
   window" → agen menganggap dirinya **offline** (`state_mgr.mark_offline()`),
   dan skor/berhenti sinkron — persis gejala "tidak update sampai di-refresh".
7. Developer sebelumnya sudah sadar ada masalah sinkronisasi dan menambah
   tombol manual **"↻ Sinkron sekarang"** (`agent/ui/server.py` route
   `/refresh`, commit `feat(kiosk): indikator koneksi + tombol sinkron`) —
   tapi tombol itu memanggil `sync_once()` yang **sama-sama** memakai jam VM
   yang salah untuk menandatangani ulang. Ia hanya membantu bila skew-nya kecil
   atau race-condition sesaat; begitu jam VM benar-benar meleset >5 menit,
   bahkan klik manual pun tidak menolong sampai jam VM itu sendiri
   dikoreksi (mis. lewat VMware Tools "Sync Time", persis yang dideskripsikan
   sebagai "refresh pada Ubuntu/VMware").

Ironisnya, **server sudah menyediakan bahan untuk memperbaiki ini sendiri**:
`GET /api/v1/state` sudah mengembalikan `server_time_ms` sejak v0.1 — tapi
field itu tidak pernah dibaca/dipakai oleh agent (`main.py` sebelumnya hanya
mengambil `status`, `active_check_codes`, dst., mengabaikan `server_time_ms`).
Infrastrukturnya sudah ada, cuma belum disambungkan.

### 2.2 Perbaikan yang Diterapkan

1. **Endpoint baru `GET /api/v1/time`** (`web/app/api/v1/time/route.ts`) —
   sengaja **tanpa signing**, supaya tidak ada masalah ayam-telur (butuh jam
   yang benar untuk sign, butuh request untuk tahu jam yang benar).
2. **`ApiClient.sync_clock()`** (`agent/network/client.py`) — dipanggil di
   awal setiap `sync_once()`, mengukur `clock_offset_ms = server_time -
   waktu_lokal` (dikompensasi separuh round-trip network), disimpan di
   `self.clock_offset_ms`. Gagal → offset lama dipertahankan (bukan direset
   ke 0), supaya satu kegagalan jaringan tidak bikin drift tiba-tiba.
3. **`build_auth_headers(..., clock_offset_ms=...)`** (`agent/crypto/signing.py`)
   — timestamp yang ditandatangani sekarang `time.time()*1000 + offset`,
   bukan jam mentah. Ini yang membuat proses **benar-benar otomatis**: tidak
   ada lagi ketergantungan pada jam sistem VM.
4. **`Runtime._now_ms()`** (`agent/main.py`) — dipakai untuk hitung
   `remaining_sec` (countdown timer di kiosk UI) dan `computed_at_ms` yang
   dikirim bersama skor, supaya timer & urutan skor juga tidak salah saat jam
   VM ngaco (sebelumnya `remaining_sec` dan `computed_at_ms` memakai jam
   lokal mentah — bug turunan dari akar masalah yang sama, mempengaruhi
   *tie-break* ranking leaderboard karena `scores.computed_at_ms` dipakai
   untuk `order by ... computed_at_ms asc` di `leaderboard` view).
5. **`SnapshotManager.build(..., now_ms=...)`** — field `taken_at_server_ms`
   pada bukti forensik snapshot sekarang benar-benar dikoreksi ke jam server,
   bukan cuma namanya yang mengklaim begitu.
6. **Admin console auto-refresh** (`web/app/admin/page.tsx`) — polling 5
   detik untuk daftar sesi, 4 detik untuk daftar peserta saat panelnya
   terbuka. Sebelumnya hanya reload manual setelah aksi (start/pause/dll.).
7. Unit test baru `tests/test_clock_skew.py` mensimulasikan jam VM meleset 30
   menit dan membuktikan: tanpa offset → request ditolak validator ala-server;
   dengan offset → lolos jendela toleransi.

**Yang sengaja TIDAK diubah**: `last_sync_sec` (indikator "N detik lalu" di
kiosk UI) tetap memakai jam lokal murni (`time.time() - self.last_sync`) —
itu mengukur *durasi berlalu*, bukan waktu absolut, jadi tidak butuh koreksi
offset sama sekali (koreksi absolut malah akan salah bila diterapkan di sini).

### 2.3 Mengapa Tombol Manual "Sinkron Sekarang" Tetap Dipertahankan

Bukan sisa bug — sengaja tetap ada sebagai *force sync* instan (mis. segera
setelah panitia klik START, peserta tak perlu menunggu siklus poll
berikutnya). Tooltip-nya sudah diperjelas agar tidak lagi disalahpahami
sebagai satu-satunya cara sinkron berjalan.

---

## 3. Review UI/UX

Klaim "tampilan masih jadul" perlu diluruskan sedikit: kode CSS yang ada
(`web/app/globals.css`) sebenarnya sudah dark-glassmorphism modern — bukan
Bootstrap default atau HTML polos. Yang sebelumnya hilang bukan *estetika
dasarnya*, tapi lapisan "terasa hidup":

- **Tidak ada indikator visual "live"** — padahal leaderboard sudah polling
  4 detik + Supabase Realtime sejak awal; user tak tahu itu tanpa mengecek
  kode. → Ditambahkan `.live-tag` + `.live-dot` (titik hijau berdenyut) di
  footer leaderboard dan header "Daftar Sesi" admin.
- **Loading state polos** (teks "Memuat…" + spinner generik) → diganti
  skeleton shimmer 3 baris di tabel leaderboard, kesan lebih premium/SaaS.
- **Tidak ada micro-interaction** pada hover kartu/baris tabel/tombol → kini
  ada transisi border, glow halus di tombol, highlight baris tabel saat hover.
- **Baris juara #1** sebelumnya cuma warna teks beda, sekarang dapat gradient
  latar halus + text-shadow emas agar benar-benar menonjol di layar besar
  (biasanya leaderboard ditampilkan di proyektor/TV).
- **Kiosk companion app** (`agent/ui/templates/index.html`) — sudah dark UI
  yang rapi sejak awal; ditambah fade-in halus per kartu dan transisi warna
  pada dot koneksi supaya perubahan status tidak "meloncat" kasar.

Yang **sengaja tidak diubah**: struktur layout, palet warna (`--acc`, `--ok`,
dst.), dan pola CSS var yang sudah dipakai konsisten di tiga permukaan (web
leaderboard, web admin, kiosk lokal) — mengganti total akan berisiko merusak
konsistensi lintas-permukaan yang justru sudah jadi kekuatan desain saat ini.

Rekomendasi UI lanjutan ada di §4.2.

---

## 4. Konsep v0.3 — Rekomendasi Lanjutan

Bagian ini murni rekomendasi (belum diimplementasikan), diprioritaskan.

### 4.1 Prioritas tinggi (keamanan & keandalan)
- **Aktifkan anti-replay nonce** (§1 temuan #3): tabel `nonces` sudah ada di
  schema tapi `verifyAgentRequest` (`web/lib/hmac.ts`) tidak pernah
  mengeceknya. Tambahkan lookup+insert `(participant_id, nonce)` sebelum
  menerima request — sekali pakai, menutup celah replay dalam jendela 5 menit.
- **Rate limit `/api/v1/admin/login`** (§1 temuan #4): mis. batas percobaan
  per IP per menit (Vercel KV / Upstash Redis, atau sederhana: kolom
  `failed_attempts` + backoff di tabel admin).
- **NTP/time-sync di level OS** (§1 temuan #5) sebagai lapisan kedua:
  meskipun perbaikan §2.2 membuat agent tahan clock-skew tanpa NTP, tetap
  disarankan menambahkan `chrony`/`systemd-timesyncd` ke `provision.sh` untuk
  layanan lain di VM (log timestamp, cron, dsb.) yang tidak melalui agent.

### 4.2 UI/UX lanjutan
- **Evidence viewer** — halaman admin untuk membuka snapshot per peserta
  (data `snapshots.artifacts`/`baseline_diff` sudah dikumpulkan agent, belum
  ada UI untuk melihatnya selain query manual ke Supabase).
- **Grafik skor per waktu** (mis. dengan Recharts) di admin — trafik
  `scores` history sudah ada di DB, tinggal divisualisasikan.
- **Dark/light theme toggle** — sibling projects (Recon/Scan) menonjolkan ini
  sebagai fitur; DHC saat ini dark-only.
- **Mode proyektor/TV** untuk leaderboard — font lebih besar, auto-hide UI
  admin link, cocok ditampilkan di layar lomba tanpa mouse.

### 4.3 Fitur organizer
- **Export hasil** (CSV/PDF) dari admin console — nama, sekolah, skor akhir,
  waktu selesai — supaya panitia tak perlu query Supabase manual untuk
  sertifikat/laporan.
- **Multi-organizer / org accounts** — saat ini satu `ADMIN_PASSWORD`
  tunggal (env var) untuk semua sesi; cocok untuk satu panitia, tidak untuk
  platform yang dipakai banyak sekolah sekaligus.

### 4.4 Keamanan tambahan
Sudah tercakup di §4.1 — nonce + rate limiting adalah dua item konkret
dengan effort kecil, dampak besar.

### 4.5 Hardening image VM
- Tambahkan `chrony` (atau NTP server lokal di jaringan lomba bila
  air-gapped) ke `provision.sh` sebagai pertahanan berlapis di samping
  perbaikan §2.2.
- Pertimbangkan mencatat `image_version` + hash baseline otomatis saat
  provisioning (sekarang manual, sesuai catatan di akhir `provision.sh`:
  "Catat image_version & hitung baseline hash sebelum export OVA").

### 4.6 Bilingual (ID/EN)
abilithic-recon & abilithic-scan menonjolkan UI bilingual Indonesia/Inggris
sebagai fitur. DHC saat ini Indonesia-only di seluruh permukaan (web, kiosk,
docs peserta). Untuk kompetisi internasional atau kontributor open-source
non-Indonesia, menambahkan toggle bahasa (mis. `next-intl` di web, dict
sederhana di kiosk HTML) akan menyamakan level dengan proyek Abilithic lain.
README sudah dibuat bilingual-style (Inggris, mengikuti pola sibling repos)
sebagai langkah pertama — UI aplikasi itu sendiri belum.

### 4.7 Testing & CI
- CI (`ci.yml`) saat ini hanya compile-check + pytest untuk agent, dan
  typecheck+build untuk web — belum ada test otomatis untuk route API
  (`web/app/api/v1/*`) atau untuk komponen React. Menambah beberapa test
  Vitest/Playwright untuk alur registrasi→start→score akan menutup gap
  regresi terbesar.
- `tests/test_clock_skew.py` (baru) sudah menutup regresi utama dari
  perbaikan ini; pertimbangkan menambahkannya ke `ci.yml` (`pytest -q` di
  root `tests/` sudah otomatis meng-include-kan file baru ini, tidak perlu
  ubah CI).

---

## 5. Penyelarasan Presentasi GitHub

Dibandingkan dengan README `abilithic-recon` & `abilithic-scan` (dicek
langsung dari GitHub org `abilithic`), README lama proyek ini punya struktur
konten yang baik tapi kurang dipoles presentasinya: tanpa badge, tanpa
logo/banner, tanpa screenshot, tanpa footer atribusi "Developed by Abil
Khosim". README sudah ditulis ulang (`README.md`) mengikuti pola yang sama:

- Header terpusat dengan logo + tagline + baris badge (License, Platform,
  Python, Next.js, Supabase, Build, LinkedIn).
- Banner horizontal di bawah tagline.
- Bagian "The Problem" sebelum fitur (pola konsisten di ketiga repo).
- Tabel System Requirements, bukan cuma daftar poin.
- Bagian Screenshots (placeholder — lihat `assets/README.md` untuk daftar
  file yang perlu ditambahkan).
- Roadmap versi.
- Comment `<!-- GitHub topics: ... -->` di akhir file (pola yang sama persis
  dipakai Recon & Scan) agar mudah disalin ke pengaturan Topics repo di
  GitHub.
- Footer "Developed by Abil Khosim" + badge LinkedIn + tagline "Security,
  built like stone." — identik dengan kedua sibling repo.
- `DISCLAIMER.md` baru (Recon & Scan masing-masing punya file ini; DHC
  sebelumnya tidak, padahal secara konten platform ini paling butuh
  disclaimer karena sengaja menanam kerentanan).

**Aksi tersisa untuk kamu** (bukan sesuatu yang bisa saya buat): taruh file
gambar aktual di folder `assets/` sesuai daftar di `assets/README.md` — begitu
file itu ada, README langsung menampilkannya tanpa edit lebih lanjut.

---

## 6. Sesi Kedua — Port, Kebersihan Repo & Penamaan File

Perubahan lanjutan sesuai permintaan: port lokal, pembersihan file, dan
struktur nama dokumen yang lebih profesional untuk GitHub.

### 6.1 Port lokal: 8080 → 9090
Kiosk/agent lokal (`localhost:8080`) diubah default ke **9090** di seluruh
kode & dokumentasi (`agent/config.example.yaml`, `agent/kiosk.py`,
`agent/main.py`, `agent/ui/server.py`, `agent/run-agent.sh`, README,
`docs/setup-participant.md`, `docs/DEPLOYMENT-GUIDE.md`) — 8080 lazim dipakai
proxy **Burp Suite / OWASP ZAP** di mesin tester/panitia, jadi dihindari agar
tak bentrok saat menjalankan agent di komputer yang sama dengan alat itu.
Entri **CHANGELOG historis** (v0.1/v0.2, yang menyebut 8080) sengaja **tidak**
diubah — itu catatan sejarah rilis yang sudah terjadi, bukan dokumentasi
perilaku saat ini.

### 6.2 Kebersihan repo untuk upload GitHub
Dicek `.gitignore` & `git ls-files`: **tidak ada** file build/cache
(`__pycache__/`, `web/.next/`, `web/node_modules/`) yang ter-*track* — sudah
bersih sejak awal, tidak ada yang perlu dihapus dari sisi git. Yang benar-benar
"tidak penting"/tidak profesional ternyata bukan file sampah, melainkan
**penamaan & lokasi dokumen**:

- `KONSEP-abilithic-defensive-competition.md` (TDD asli, 1000+ baris) hidup
  **di luar repo git** (satu folder di atas), sehingga **tidak pernah
  ter-upload ke GitHub** — dan README lama/baru sempat mereferensikannya
  dengan link yang salah. **Dipindahkan** (disalin, isi tidak diubah) ke
  `docs/TECHNICAL-DESIGN.md` di dalam repo. File asli di luar repo **sengaja
  dibiarkan ada** di komputer kamu — hapus sendiri kalau sudah yakin tidak
  dibutuhkan lagi di luar repo.
- `PANDUAN-SETUP-v0.1.md` (panduan deployment dari nol) dipindah ke
  `docs/DEPLOYMENT-GUIDE.md`, judul & isinya disunting agar tak lagi menyebut
  "v0.1"/"5 celah" (sudah 15 celah & 3 tingkat sejak v0.2), dan baris penutup
  yang terlalu personal ("aku bantu urai...") diganti jadi arahan standar
  (buka issue GitHub).
- Dokumen review ini sendiri dipindah dari root (`REVIEW-DAN-KONSEP-v2.md`,
  nama campur bahasa) ke `docs/REVIEW-AND-CONCEPT-v2.md` — konsisten dengan
  `docs/V0.2-PLAN.md` dan bahasa Inggris yang dipakai README/badge.

Struktur root repo sekarang lebih ramping: hanya file governance standar
GitHub (`README`, `LICENSE`, `CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`,
`DISCLAIMER`, `CHANGELOG`) yang tersisa di root; semua dokumen teknis/naratif
panjang ada di `docs/`.

---

## 7. Ringkasan Perubahan Kode (Kedua Sesi)

| File | Perubahan |
|---|---|
| `web/app/api/v1/time/route.ts` | **Baru** — endpoint publik jam server |
| `agent/crypto/signing.py` | `build_auth_headers` menerima `clock_offset_ms` |
| `agent/network/client.py` | `ApiClient.sync_clock()` + offset dipakai di semua request signed |
| `agent/main.py` | `Runtime._now_ms()`, dipakai untuk timer/skor/snapshot; `sync_once()` panggil `sync_clock()` lebih dulu; default port 9090 |
| `agent/snapshot/manager.py` | `build(..., now_ms=...)` — snapshot pakai jam terkoreksi |
| `tests/test_clock_skew.py` | **Baru** — 3 test regresi clock-skew |
| `web/app/admin/page.tsx` | Auto-refresh sesi (5s) & peserta (4s); indikator "Auto-refresh" |
| `web/app/page.tsx` | Skeleton loading, indikator "Live" |
| `web/app/globals.css` | `.live-dot`/`.live-tag`, skeleton shimmer, micro-interaction hover/transisi, highlight baris juara #1 |
| `agent/ui/templates/index.html` | Fade-in kartu, transisi dot koneksi, tooltip tombol sinkron diperjelas |
| `agent/config.example.yaml`, `agent/kiosk.py`, `agent/ui/server.py`, `agent/run-agent.sh` | Port default 8080 → 9090 |
| `README.md` | Ditulis ulang mengikuti pola abilithic-recon/abilithic-scan; link ke `docs/` diperbarui |
| `DISCLAIMER.md`, `assets/README.md` | **Baru** |
| `docs/TECHNICAL-DESIGN.md` | **Baru** — TDD asli dipindahkan ke dalam repo |
| `docs/REVIEW-AND-CONCEPT-v2.md` | **Baru** — dokumen ini, dipindah dari root |
| `docs/DEPLOYMENT-GUIDE.md` | **Baru** — dipindah & disunting dari `PANDUAN-SETUP-v0.1.md` |
| `docs/setup-participant.md` | Port 8080 → 9090 |

Semua perubahan Python diverifikasi `py_compile` + unit test manual (pytest
tidak tersedia offline di sandbox verifikasi, jadi test dijalankan langsung
via runner manual). Perubahan TypeScript/TSX diverifikasi dengan `tsc
--noEmit` memakai `node_modules` proyek yang sudah ter-install; hasil: 0
error di kedua pemeriksaan.
