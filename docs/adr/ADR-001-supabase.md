# ADR-001 — Memakai Supabase (bukan backend sendiri)

**Status:** Accepted · 2026-06-30

## Context
Butuh database, realtime leaderboard, auth, dan penyimpanan evidence dengan biaya nol
dan operasi seminimal mungkin (proyek dijalankan panitia sekolah, bukan tim infra).

## Decision
Pakai **Supabase** (Postgres + Realtime + Auth + Storage) di free tier. Web (Next.js)
di Vercel. API `/v1` sebagai Next.js route handlers yang menulis ke Supabase via service role.

## Consequences
- (+) Gratis, satu platform untuk DB/realtime/auth/storage; cepat dibangun.
- (+) Realtime leaderboard tanpa server WebSocket sendiri.
- (−) Batas free tier (koneksi/Realtime) → target ≤300 peserta/sesi; upgrade bila lebih (lihat TDD §23, §39).
