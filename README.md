<div align="center">

# abilithic DHC
### Defensive Hardening Competition Platform
**Defend. Harden. Compete.**

Platform lomba keamanan siber **defensif (blue-team / system hardening)** yang gratis & open source.
Peserta mengamankan VM Ubuntu yang sengaja dibuat rentan, skor dinilai **otomatis & realtime**.

[Konsep / TDD lengkap](../KONSEP-abilithic-defensive-competition.md) · [Setup Peserta](docs/setup-participant.md) · [API Contract](docs/api-contract.md) · [ADR](docs/adr)

</div>

---

## ✨ Apa ini?

Mirip **CyberPatriot**, tapi open source dan mudah di-deploy. Bukan CTF "serang" — ini **bertahan**:
peserta memperbaiki celah keamanan (hardening) pada server Ubuntu dalam batas waktu, dan setiap
perbaikan benar otomatis menambah skor yang tampil **live** di papan skor.

- 🎯 **Tingkat kesulitan umum**: Mudah / Medium / Hard (dipilih panitia per lomba)
- ⚖️ **Adil & berbukti**: Baseline & Evidence System menutup celah "memperbaiki sebelum START"
- 🆓 **100% gratis**: Vercel (web) + Supabase (DB/Realtime/Auth) + agen Python
- 🧩 **Modular**: tambah check baru tanpa menyentuh engine (plugin-style)

## 🏗️ Arsitektur (ringkas)

```
[ VM Ubuntu peserta + abilithic-agent ] --HTTPS--> [ Next.js /v1 API ] --> [ Supabase: DB + Realtime ]
                                                                                      |
                                                                            [ Web: Leaderboard + Admin ]
```
Agen di balik NAT → **polling keluar** (server tak menghubungi agen). Detail: [TDD](../KONSEP-abilithic-defensive-competition.md).

## 📁 Struktur Repo

```
db/       Schema Postgres + seed (difficulties + 5 check)
agent/    Agen Python modular (engine, checks, network, snapshot, crypto, ui)
web/      Next.js (API /v1 + Leaderboard realtime + Admin START/STOP)
docs/     Dokumentasi + ADR
tests/    Unit test (scoring engine)
```

## 🚀 Quickstart (v0.1 / MVP)

### 1. Database (Supabase)
1. Buat project gratis di [supabase.com](https://supabase.com).
2. Buka **SQL Editor**, jalankan `db/schema.sql`, lalu `db/seed/difficulties.sql`.
3. Catat **Project URL**, **anon key**, dan **service_role key** (Settings → API).

### 2. Web Portal (Next.js)
```bash
cd web
cp .env.example .env.local      # isi kredensial Supabase + AGENT_HMAC_SECRET
npm install
npm run dev                     # http://localhost:3000
```
Deploy ke Vercel: import repo → set folder root `web/` → isi Environment Variables.

### 3. Agent (di dalam VM Ubuntu peserta)
```bash
cd agent
cp config.example.yaml config.yaml   # set portal_url ke URL web kamu
pip install -r requirements.txt
sudo python3 main.py                 # buka http://localhost:8080 untuk registrasi
```

### 4. Jalankan lomba
1. Di **/admin** (web): buat sesi, pilih tingkat **Mudah**, dapatkan **kode sesi**.
2. Peserta registrasi di `localhost:8080` pakai kode sesi.
3. Admin klik **START** → semua agen menilai serentak → skor live di **/** (leaderboard).
4. **STOP** → skor beku → export hasil.

## 🧪 Test
```bash
cd tests && python3 -m pytest -q          # unit test scoring engine
```

## 🗺️ Roadmap
v0.1 MVP (Easy, 5 check) → v0.2 (3 tingkat, hints, evidence viewer, penalty) → v0.3 (plugin, agen Go) → v0.4 Windows → v1.0 production. Lihat [TDD §29](../KONSEP-abilithic-defensive-competition.md).

## 🤝 Kontribusi & Keamanan
Lihat [CONTRIBUTING.md](CONTRIBUTING.md) · Lapor celah keamanan via [SECURITY.md](SECURITY.md) (jangan via issue publik).

## 📄 Lisensi
[MIT](LICENSE) © 2026 abilithic.
