-- =====================================================================
-- abilithic DHC — Seed data (v0.2)
-- 15 check Linux + preset tingkat (Easy 6 / Medium 11 / Hard 15).
-- AMAN dijalankan ulang: memakai UPSERT (on conflict do update),
-- jadi menjalankan lagi akan MEMPERBARUI check & preset yang sudah ada.
-- Jalankan SETELAH schema.sql.
-- =====================================================================

-- ---------------- 15 CHECK ----------------
insert into checks (code, title, description, points, is_penalty, must_stay_passing, category, hint_basic, hint_advanced, difficulty_tags) values
  ('ssh_root_disabled','Nonaktifkan SSH root login','PermitRootLogin harus "no".',10,false,false,'ssh',
    'Periksa /etc/ssh/sshd_config baris PermitRootLogin.','Set "PermitRootLogin no" lalu: sudo systemctl restart ssh','["easy","medium","hard"]'),
  ('ufw_enabled','Aktifkan firewall UFW','Firewall UFW harus active.',10,false,false,'firewall',
    'Cek: sudo ufw status','Aktifkan: sudo ufw enable','["easy","medium","hard"]'),
  ('telnet_disabled','Matikan layanan Telnet','Tidak boleh ada layanan di port 23.',10,false,false,'service',
    'Cek layanan port 23 (telnet).','Disable & hapus: sudo systemctl disable --now inetd; sudo apt purge telnetd','["easy","medium","hard"]'),
  ('rogue_user_removed','Hapus akun tak sah','Akun "hacker" harus dihapus.',10,false,false,'account',
    'Periksa daftar user di /etc/passwd.','Hapus: sudo deluser --remove-home hacker','["easy","medium","hard"]'),
  ('shadow_perm','Perbaiki permission /etc/shadow','/etc/shadow tidak boleh world-readable (mode 640).',10,false,false,'permission',
    'Cek: ls -l /etc/shadow','Perbaiki: sudo chmod 640 /etc/shadow','["easy","medium","hard"]'),
  ('passwd_perm','Perbaiki permission /etc/passwd','/etc/passwd mode 644 (tak writable group/other).',10,false,false,'permission',
    'Cek: ls -l /etc/passwd','Perbaiki: sudo chmod 644 /etc/passwd','["easy","medium","hard"]'),
  ('empty_password_removed','Hapus akun password kosong','Tak boleh ada akun login berpassword kosong.',10,false,false,'account',
    'Cek /etc/shadow field password kosong.','Kunci/hapus: sudo passwd -l <user>','["medium","hard"]'),
  ('uid0_unique','Hanya root ber-UID 0','Tak boleh akun lain ber-UID 0.',10,false,false,'account',
    'Cek UID 0 di /etc/passwd.','Hapus akun UID 0 palsu: sudo userdel <user>','["medium","hard"]'),
  ('ip_forward_disabled','Matikan IP forwarding','net.ipv4.ip_forward harus 0.',10,false,false,'network',
    'Cek: cat /proc/sys/net/ipv4/ip_forward','Matikan: sudo sysctl -w net.ipv4.ip_forward=0','["medium","hard"]'),
  ('password_max_days','Batasi umur password','PASS_MAX_DAYS <= 365 di /etc/login.defs.',10,false,false,'policy',
    'Cek /etc/login.defs PASS_MAX_DAYS.','Set PASS_MAX_DAYS 365','["medium","hard"]'),
  ('ssh_permitempty_disabled','Larang SSH password kosong','PermitEmptyPasswords harus "no".',10,false,false,'ssh',
    'Cek /etc/ssh/sshd_config PermitEmptyPasswords.','Set no lalu: sudo systemctl restart ssh','["medium","hard"]'),
  ('world_writable_removed','Amankan file world-writable','/opt/dhc/secret.txt tak boleh world-writable.',10,false,false,'permission',
    'Cek: ls -l /opt/dhc/secret.txt','Perbaiki: sudo chmod 644 /opt/dhc/secret.txt','["hard"]'),
  ('suid_bash_removed','Hapus SUID shell berbahaya','Backdoor SUID /usr/local/bin/rootbash harus dihapus.',10,false,false,'privilege',
    'Cek: ls -l /usr/local/bin/rootbash','Hapus: sudo rm -f /usr/local/bin/rootbash','["hard"]'),
  ('rogue_sudo_removed','Cabut sudo tak sah','Akun "backdoor" tak boleh di grup sudo.',10,false,false,'privilege',
    'Cek: getent group sudo','Cabut: sudo gpasswd -d backdoor sudo','["hard"]'),
  ('cron_backdoor_removed','Hapus cron backdoor','/etc/cron.d/dhc-backdoor harus dihapus.',10,false,false,'persistence',
    'Periksa /etc/cron.d/.','Hapus: sudo rm -f /etc/cron.d/dhc-backdoor','["hard"]')
on conflict (code) do update set
  title=excluded.title, description=excluded.description, points=excluded.points,
  is_penalty=excluded.is_penalty, must_stay_passing=excluded.must_stay_passing,
  category=excluded.category, hint_basic=excluded.hint_basic,
  hint_advanced=excluded.hint_advanced, difficulty_tags=excluded.difficulty_tags;

-- ---------------- PRESET TINGKAT (subset berbeda) ----------------
insert into difficulties (key, name, description, active_check_codes, hint_policy, penalty_weight, default_duration_sec) values
  ('easy','Mudah','Lomba perdana/pemula. 6 soal dasar, hint lengkap, penalti ringan.',
    '["ssh_root_disabled","ufw_enabled","telnet_disabled","rogue_user_removed","shadow_perm","passwd_perm"]',
    'full', 0.5, 7200),
  ('medium','Medium','Peserta terbiasa. 11 soal, hint terbatas, penalti standar.',
    '["ssh_root_disabled","ufw_enabled","telnet_disabled","rogue_user_removed","shadow_perm","passwd_perm","empty_password_removed","uid0_unique","ip_forward_disabled","password_max_days","ssh_permitempty_disabled"]',
    'limited', 1.0, 5400),
  ('hard','Hard','Peserta mahir. 15 soal (termasuk backdoor tersembunyi), hint minim, penalti berat.',
    '["ssh_root_disabled","ufw_enabled","telnet_disabled","rogue_user_removed","shadow_perm","passwd_perm","empty_password_removed","uid0_unique","ip_forward_disabled","password_max_days","ssh_permitempty_disabled","world_writable_removed","suid_bash_removed","rogue_sudo_removed","cron_backdoor_removed"]',
    'none', 1.5, 3600)
on conflict (key) do update set
  name=excluded.name, description=excluded.description,
  active_check_codes=excluded.active_check_codes, hint_policy=excluded.hint_policy,
  penalty_weight=excluded.penalty_weight, default_duration_sec=excluded.default_duration_sec;
