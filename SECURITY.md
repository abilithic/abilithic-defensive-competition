# Security Policy

## Responsible Disclosure

BlueForge adalah proyek **keamanan siber**, jadi kami menanggapi laporan celah dengan serius.

**Jangan** melaporkan celah keamanan melalui GitHub Issue publik.

Sebaliknya, kirim email ke: **security@blueforge.example** (ganti dengan email resmi kamu)
dengan detail:
- Deskripsi celah & dampaknya
- Langkah reproduksi
- Versi/komponen yang terdampak (web / agent / db)

Kami akan merespons dalam **72 jam** dan berkoordinasi soal perbaikan & pengungkapan.

## Cakupan

| Komponen | Contoh isu yang dicari |
|---|---|
| Agent | bypass scoring, pemalsuan HMAC, kebocoran answer-key |
| Web/API | auth bypass, IDOR, injeksi, kebocoran token |
| DB | RLS lemah, kebocoran evidence |

## Catatan tahap MVP (v0.1)

v0.1 memakai keamanan ringan (HTTPS + token + HMAC + baseline). Fitur berat
(split-key, certificate pinning, replay protection penuh, rotasi token) menyusul di
fase produksi — lihat TDD §37. Laporan tetap kami hargai.
