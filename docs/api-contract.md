# API Contract `/v1` (ringkas)

Detail lengkap + contoh JSON ada di **TDD §16**. Implementasi: `web/app/api/v1/*`.

| Endpoint | Auth | Fungsi |
|---|---|---|
| `POST /api/v1/register` | kode sesi | Registrasi peserta → `participant_id`, `agent_token`, `agent_secret` |
| `GET /api/v1/state` | HMAC | Tarik status lomba + `active_check_codes` + `ends_at_ms` |
| `POST /api/v1/score` | HMAC | Kirim skor (hanya saat `running`) |
| `POST /api/v1/snapshot` | HMAC | Kirim evidence (registration/start/stop); START → hitung `eligible` |
| `POST /api/v1/heartbeat` | HMAC | Tanda hidup + versi agent |
| `GET /api/v1/leaderboard` | publik | Data papan skor |
| `GET/POST /api/v1/admin/competitions` | password admin | Kelola sesi + START/PAUSE/STOP |

## Header signing (endpoint agen)
```
X-Participant, X-Timestamp, X-Nonce, X-Signature
Signature = HMAC-SHA256(agent_secret, METHOD\nPATH\nBODY\nTS\nNONCE)
```
`agent_secret = HMAC-SHA256(AGENT_HMAC_SECRET, participant_id)` (server menghitung ulang).

## Kode status (TDD §17)
`200` ok · `400` payload salah · `401` signature/timestamp invalid · `403` admin salah ·
`404` sesi tak ada · `409` sesi belum/ sudah selesai (skor diabaikan) · `429` rate limit · `5xx` retry.
