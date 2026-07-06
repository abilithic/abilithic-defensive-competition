#!/usr/bin/env python3
"""abilithic DHC — simulasi service Telnet (SENGAJA rentan, soal #3 `telnet_disabled`).

Kenapa file ini ada: paket `telnetd`/`inetutils-telnetd` klasik sering sudah
tidak tersedia atau tidak bisa jalan lewat systemd di rilis Ubuntu modern
(termasuk 26.04) — sehingga soal ini kadang "PASS sendiri" tanpa peserta
berbuat apa-apa, karena tidak pernah ada apa pun yang benar-benar listen di
port 23. Itu bukan bug agent, tapi bug provisioning: soalnya jadi gratis.

Solusinya: listener TCP minimal ini, dijalankan sebagai service systemd
(`dhc-telnetd.service`), SELALU bisa jalan di Ubuntu versi berapa pun karena
cuma pakai modul `socket` bawaan Python — tidak bergantung paket telnet apa
pun. Ini BUKAN implementasi protokol Telnet sungguhan (tidak ada negosiasi
IAC/opsi) — cukup socket yang menerima koneksi & mengirim banner login palsu,
karena `agent/checks/telnet_disabled/check.py` HANYA menguji status LISTEN
di port TCP 23 (meniru cara benchmark hardening menilai "servis apa saja yang
berjalan di port berbahaya"), bukan menguji kebenaran protokolnya.

Peserta WAJIB mematikan lewat systemd (bukan cuma bunuh proses), supaya tidak
otomatis nyala lagi setelah reboot:
    sudo systemctl disable --now dhc-telnetd
"""
import socket

HOST, PORT = "0.0.0.0", 23
BANNER = b"Ubuntu 26.04 LTS\r\nlogin: "


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(20)
    while True:
        conn, _addr = srv.accept()
        try:
            conn.sendall(BANNER)
        except Exception:
            pass
        finally:
            conn.close()


if __name__ == "__main__":
    main()
