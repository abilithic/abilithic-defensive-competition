# Contributing to BlueForge

Terima kasih sudah tertarik berkontribusi! 🎉

## Prinsip utama

1. **Patuhi kontrak stabil (TDD §27).** Perubahan harus *additive*. Jangan ubah arti `code` check,
   field API `/v1`, atau format snapshot yang sudah ada.
2. **Scoring engine = pure function.** Setiap perubahan wajib disertai/lulus unit test (`tests/`).
3. **Jangan over-engineering.** Ikuti prioritas fitur TDD §36 (MVP → Nice → Future).

## Menambah check baru (paling umum)

Tambah folder di `agent/checks/<code>/`:
```
agent/checks/<code>/
├── manifest.yaml     # code (unik & stabil), title, points, hints, difficulty_tags
└── check.py          # fungsi run(ctx) -> {"passed": bool, "evidence": {...}}
```
Lalu tambahkan `code` ke `active_check_codes` pada seed/preset tingkat di `db/seed/difficulties.sql`.
**Tidak perlu menyentuh engine.**

## Alur PR

1. Fork & branch: `feat/<ringkas>` atau `fix/<ringkas>`.
2. Pastikan lint & test hijau: `cd tests && pytest -q`.
3. Update `CHANGELOG.md` (format Keep a Changelog).
4. Buka PR memakai template; jelaskan *apa* & *kenapa*.

## Gaya kode

- **Python**: PEP8, modul kecil single-responsibility (lihat `agent/` per modul).
- **TypeScript/Next.js**: komponen kecil, tipe di `web/lib`/`types`.
- Pesan commit: imperatif singkat (mis. `add ufw check`, `fix score idempotency`).

## Decision Records

Keputusan arsitektur besar didokumentasikan di `docs/adr/`. Bila kamu mengusulkan
perubahan arsitektur, tambahkan ADR baru (format: Context → Decision → Consequences → Status).
