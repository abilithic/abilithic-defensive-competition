# Panduan Peserta — Setup VM & Agent

## 1. Persiapan (sebelum hari-H)

1. **Install VMware Workstation Player** (gratis) atau VirtualBox.
2. **Unduh image VM** BlueForge dari link yang diberikan panitia (file `.ova`).
   - Verifikasi integritas: cocokkan **SHA256** file dengan yang diumumkan panitia.
3. **Import** file `.ova` ke VMware: `File → Open → pilih .ova → Import`.
4. Jalankan VM minimal sekali untuk memastikan booting normal. **Jangan** mengubah apa pun dulu.

## 2. Saat hari-H

1. Nyalakan VM dan pastikan **terhubung internet** (NAT/Bridged).
2. Di dalam VM, buka browser ke **http://localhost:9090** (UI agent).
3. Isi **Nama**, **Sekolah**, dan **Kode Sesi** (dibagikan panitia), klik **Daftar**.
4. Tunggu panitia menekan **START**. Timer & daftar tugas akan muncul otomatis.
5. Lakukan **hardening**. Setiap perbaikan benar menambah skor — pantau di:
   - `localhost:9090` (status pribadi + hint), dan
   - papan skor publik (URL dari panitia).
6. Saat waktu habis, skor otomatis **dibekukan**. Perbaikan setelah itu tidak dihitung.

## 3. Tips

- Jangan mematikan layanan yang wajib hidup (mis. SSH resmi) — ada **penalti**.
- Hint tersedia sesuai tingkat: **Mudah** (lengkap), **Medium** (terbatas), **Hard** (minim).
- Jika internet sempat putus, agent menyimpan skor lokal dan mengirim ulang saat tersambung lagi.

## 4. Troubleshooting

| Masalah | Solusi |
|---|---|
| `localhost:9090` tak terbuka | Pastikan agent jalan: `sudo systemctl status blueforge-agent` |
| "Kode sesi tidak ditemukan" | Pastikan kode benar & panitia sudah membuat sesi |
| Skor tak naik | Cek hint di `localhost:9090`; mungkin perbaikan belum sesuai |
