# ADR-002 — Agen memakai Polling (bukan push ke agen)

**Status:** Accepted · 2026-06-30

## Context
VM peserta berada di balik NAT (jaringan rumah/sekolah) tanpa IP publik. Server di
internet tidak bisa membuka koneksi masuk ke agen.

## Decision
**Agen menarik (polling)** state dari server lewat `GET /v1/state` secara berkala,
lalu mengirim skor/snapshot via POST. Server tidak pernah menghubungi agen.

## Consequences
- (+) Bekerja di balik NAT tanpa konfigurasi jaringan.
- (+) Sederhana & tahan jaringan buruk (retry + store-and-forward).
- (−) Ada latensi hingga 1 interval polling saat START; dimitigasi sinkronisasi `started_at`/`ends_at`.
