# Disclaimer

**BlueForge** sengaja menanam celah keamanan (SSH root login, firewall
mati, akun rogue, SUID backdoor, dll — lihat `image/build/provision.sh`) ke
dalam VM Ubuntu agar peserta berlatih *hardening*. Ini dibuat **khusus untuk
pelatihan defensif di lingkungan terisolasi**, bukan untuk produksi.

Dengan menjalankan platform ini kamu setuju bahwa:

- VM yang di-provision dengan `provision.sh` **hanya boleh berjalan di
  jaringan lomba yang terisolasi** (VMware host-only / air-gapped), tidak
  pernah diekspos ke internet publik atau jaringan produksi.
- Kamu bertanggung jawab penuh atas keamanan infrastruktur (Supabase project,
  deployment Vercel, `AGENT_HMAC_SECRET`, `ADMIN_PASSWORD`) yang kamu jalankan
  sendiri.
- Proyek ini disediakan **apa adanya** ("as is"), tanpa jaminan apa pun — lihat
  [LICENSE](LICENSE) (MIT).
- Untuk penggunaan edukatif/pelatihan keamanan siber yang sah. Jangan
  menerapkan celah yang sama pada sistem yang menyimpan data nyata atau
  digunakan oleh orang lain tanpa izin eksplisit.

Bila menemukan celah pada platform itu sendiri (bukan celah yang memang
sengaja ditanam untuk lomba), laporkan lewat [SECURITY.md](SECURITY.md) —
jangan lewat issue publik.
