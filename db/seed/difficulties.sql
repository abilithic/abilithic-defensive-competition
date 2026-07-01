-- =====================================================================
-- abilithic DHC — Seed data (v0.1)
-- Preset tingkat kesulitan + 5 check Linux dasar (TDD §6, §36, §40)
-- Jalankan SETELAH schema.sql
-- =====================================================================

-- ---------------- 5 CHECK LINUX DASAR (MVP) ----------------
insert into checks (code, title, description, points, is_penalty, must_stay_passing, category, hint_basic, hint_advanced, difficulty_tags)
values
  ('ssh_root_disabled',
   'Nonaktifkan SSH root login',
   'PermitRootLogin harus diset "no" di /etc/ssh/sshd_config.',
   10, false, false, 'ssh',
   'Periksa file /etc/ssh/sshd_config pada baris PermitRootLogin.',
   'Set "PermitRootLogin no" lalu jalankan: sudo systemctl restart ssh',
   '["easy","medium","hard"]'),

  ('ufw_enabled',
   'Aktifkan firewall UFW',
   'Firewall UFW harus berstatus active.',
   10, false, false, 'firewall',
   'Cek status firewall dengan: sudo ufw status',
   'Aktifkan dengan: sudo ufw enable',
   '["easy","medium","hard"]'),

  ('telnet_disabled',
   'Matikan layanan Telnet',
   'Telnet tidak aman dan tidak boleh listen di port 23.',
   10, false, false, 'service',
   'Cek apakah ada layanan di port 23 (telnet).',
   'Hentikan & disable: sudo systemctl disable --now inetd/telnetd, atau hapus paket telnetd.',
   '["easy","medium","hard"]'),

  ('rogue_user_removed',
   'Hapus akun tak sah',
   'Akun mencurigakan "hacker" harus dihapus dari sistem.',
   10, false, false, 'account',
   'Periksa daftar user di /etc/passwd.',
   'Hapus user: sudo deluser --remove-home hacker',
   '["easy","medium","hard"]'),

  ('shadow_perm',
   'Perbaiki permission /etc/shadow',
   'File /etc/shadow tidak boleh world-readable (mode 640 atau lebih ketat).',
   10, false, false, 'permission',
   'Cek permission: ls -l /etc/shadow',
   'Perbaiki: sudo chmod 640 /etc/shadow',
   '["easy","medium","hard"]')
on conflict (code) do nothing;

-- ---------------- PRESET TINGKAT KESULITAN ----------------
-- Easy: 5 check dasar, hint penuh, penalti ringan, durasi longgar
insert into difficulties (key, name, description, active_check_codes, hint_policy, penalty_weight, default_duration_sec)
values
  ('easy',
   'Mudah',
   'Untuk lomba perdana / pemula. Hint lengkap, penalti ringan.',
   '["ssh_root_disabled","ufw_enabled","telnet_disabled","rogue_user_removed","shadow_perm"]',
   'full', 0.5, 7200),

  ('medium',
   'Medium',
   'Untuk peserta yang sudah terbiasa. Hint terbatas, penalti standar.',
   '["ssh_root_disabled","ufw_enabled","telnet_disabled","rogue_user_removed","shadow_perm"]',
   'limited', 1.0, 5400),

  ('hard',
   'Hard',
   'Untuk peserta mahir. Hint minim, penalti berat.',
   '["ssh_root_disabled","ufw_enabled","telnet_disabled","rogue_user_removed","shadow_perm"]',
   'none', 1.5, 3600)
on conflict (key) do nothing;

-- Catatan: di v0.2+ subset check Medium/Hard diperbanyak (10+/18+) lewat
-- penambahan baris checks + update active_check_codes. Inti tak berubah (TDD §27).
