#!/usr/bin/env python3
"""abilithic DHC — Kiosk launcher.

Menjalankan agent (main.py) di latar, menunggu UI lokal siap, lalu membuka
UI itu sebagai **jendela aplikasi companion** (BUKAN fullscreen-lock), supaya
peserta tetap bisa membuka Terminal & bekerja (hardening) sambil melihat skor.

Urutan mode tampilan (pakai yang pertama tersedia):
  1) pywebview  -> jendela native app (tanpa browser chrome)
  2) chromium/chrome --app / firefox --new-window (fallback andal)

Jalankan: python3 kiosk.py   (biasanya dipanggil otomatis oleh autostart)

CATATAN "jendela blank setelah restart VM" (dua penyebab, dua fix):
  1) WebKitGTK (backend pywebview di Linux) punya bug dikenal luas: renderer
     DMA-BUF-nya sering gagal total (window terbuka tapi BENAR-BENAR blank/
     putih) di GPU virtual VMware/VirtualBox/QEMU. Fix resminya set env
     WEBKIT_DISABLE_DMABUF_RENDERER=1 (+ WEBKIT_DISABLE_COMPOSITING_MODE=1)
     SEBELUM proses WebKit dibuat -> makanya diset di baris paling atas file
     ini, sebelum `import webview` (yang baru memicu init GTK/WebKit).
  2) Race condition: dulu kalau UI lokal (Flask) belum sempat nyala saat
     window dibuka (VM baru boot = jaringan/servis masih "pemanasan"),
     pywebview tetap memuat URL sekali saja lalu MENYERAH (tidak retry) ->
     hasilnya tampilan kosong/connection-error yang terlihat "blank". Fix:
     window sekarang dibuka dengan halaman loading LOKAL dulu (tidak perlu
     server nyala), lalu background thread mem-poll sampai UI siap baru
     window dialihkan ke URL asli (lihat open_pywebview()).
"""
import os

# HARUS di baris paling atas, sebelum "import webview" mana pun memicu init
# GTK/WebKit -- lihat catatan di docstring di atas.
os.environ.setdefault("WEBKIT_DISABLE_DMABUF_RENDERER", "1")
os.environ.setdefault("WEBKIT_DISABLE_COMPOSITING_MODE", "1")

import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 9090  # harus sama dengan local_ui_port di config.yaml (bukan 8080 — hindari bentrok Burp Suite/ZAP)
URL = f"http://127.0.0.1:{PORT}"

LOADING_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  html,body{margin:0;height:100%;background:#0a0e1a;color:#eef2fb;
    font-family:-apple-system,Segoe UI,Roboto,sans-serif;
    display:flex;align-items:center;justify-content:center;flex-direction:column}
  .dot{width:14px;height:14px;border-radius:50%;background:#5b8cff;margin-bottom:18px;
    animation:pulse 1.1s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:.35;transform:scale(.85)}50%{opacity:1;transform:scale(1)}}
  p{color:#8a97b4;font-size:13px;margin:4px 0}
  b{color:#eef2fb}
</style></head><body>
  <div class="dot"></div>
  <p><b>abilithic DHC</b></p>
  <p id="msg">Menghubungkan ke agent lokal...</p>
</body></html>"""

ERROR_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  html,body{margin:0;height:100%;background:#0a0e1a;color:#eef2fb;
    font-family:-apple-system,Segoe UI,Roboto,sans-serif;
    display:flex;align-items:center;justify-content:center;flex-direction:column;
    text-align:center;padding:24px;box-sizing:border-box}
  p{color:#8a97b4;font-size:13px;line-height:1.6}
  b{color:#ff5d5d}
</style></head><body>
  <p><b>Agent lokal tidak merespons.</b><br/>
  Buka terminal dan cek: <code>sudo python3 main.py</code><br/>
  atau coba lagi lewat browser: http://localhost:9090</p>
</body></html>"""

_agent_proc = None


def _agent_already_running():
    """Cek apakah UI lokal sudah dilayani pihak lain (mis. systemd service
    `abilithic-agent`, yang normalnya jalan terus-menerus di instalasi
    kiosk). Kalau sudah, kiosk.py TIDAK BOLEH menjalankan main.py sendiri --
    dua proses main.py rebutan port 9090 menyebabkan salah satunya gagal
    bind ("Address already in use") dan bisa membuat UI/registrasi
    berperilaku aneh (window kadang bicara ke proses yang salah/baru saja
    crash)."""
    try:
        with urllib.request.urlopen(URL, timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def start_agent():
    """Jalankan agent (main.py) sebagai proses terpisah -- HANYA kalau belum
    ada yang melayani port 9090 (lihat _agent_already_running()). Di
    instalasi kiosk normal, `abilithic-agent.service` (systemd) yang
    menjalankan main.py; kiosk.py di sini murni menampilkan jendelanya saja.
    Kalau dijalankan berdiri sendiri saat development (tanpa systemd
    service), kiosk.py tetap akan menjalankan main.py sendiri seperti
    biasa."""
    global _agent_proc
    if _agent_already_running():
        print("[kiosk] agent lokal sudah melayani port 9090 (mis. via "
              "systemd abilithic-agent) -- tidak menjalankan salinan baru.",
              flush=True)
        return None
    py = sys.executable or "python3"
    _agent_proc = subprocess.Popen([py, os.path.join(HERE, "main.py")])
    return _agent_proc


def wait_ui(timeout=120):
    """Tunggu sampai UI lokal merespons.

    Default dinaikkan ke 120s (dari 40s) -- setelah restart VM, network
    manager/DNS/dsb. bisa lambat "pemanasan" beberapa puluh detik sebelum
    agent benar-benar siap; 40s sebelumnya kadang keburu timeout dan bikin
    window kiosk terlihat blank/gagal padahal agent sebenarnya cuma telat
    sedikit.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(URL, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def stop_agent():
    if _agent_proc and _agent_proc.poll() is None:
        try:
            _agent_proc.terminate()
            _agent_proc.wait(timeout=5)
        except Exception:
            try:
                _agent_proc.kill()
            except Exception:
                pass


def open_pywebview():
    """Jendela aplikasi companion. Return True bila berhasil dibuka.

    Dibuka dengan halaman loading LOKAL dulu (html=..., tak butuh server
    nyala sama sekali) supaya window TIDAK PERNAH blank walau agent belum
    siap -- lalu thread latar mem-poll UI lokal dan mengalihkan window ke
    URL asli begitu siap. Ini menghilangkan race condition "server belum
    nyala saat window dibuka" yang sebelumnya bisa terlihat sebagai jendela
    kosong setelah restart VM.
    """
    try:
        import webview  # pywebview
    except Exception:
        return False
    try:
        window = webview.create_window("abilithic DHC", html=LOADING_HTML,
                                        width=460, height=880, resizable=True,
                                        background_color="#0a0e1a")

        def _wait_then_load():
            if wait_ui():
                window.load_url(URL)
            else:
                print("[kiosk] UI lokal tidak siap dalam batas waktu.", flush=True)
                window.load_html(ERROR_HTML)

        webview.start(_wait_then_load)
        return True
    except Exception as e:
        print(f"[kiosk] pywebview gagal: {e}", flush=True)
        return False


def open_browser_kiosk():
    """Fallback: buka browser terpasang sebagai jendela app (bukan kiosk-lock)."""
    candidates = [
        ["chromium-browser", f"--app={URL}", "--window-size=460,880", "--no-first-run"],
        ["chromium", f"--app={URL}", "--window-size=460,880", "--no-first-run"],
        ["google-chrome", f"--app={URL}", "--window-size=460,880", "--no-first-run"],
        ["google-chrome-stable", f"--app={URL}", "--window-size=460,880", "--no-first-run"],
        ["firefox", "--new-window", URL],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            print(f"[kiosk] membuka via {cmd[0]}", flush=True)
            proc = subprocess.Popen(cmd)
            proc.wait()
            return True
    if shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", URL])
        while True:
            time.sleep(3600)
    return False


def _pywebview_available():
    try:
        import webview  # noqa: F401
        return True
    except Exception:
        return False


def main():
    print("[kiosk] menjalankan agent...", flush=True)
    start_agent()
    # PENTING: jangan wait_ui() di sini dulu untuk jalur pywebview -- window
    # pywebview membuka halaman loading LOKAL secara instan (lihat
    # open_pywebview()) lalu menunggu di background thread-nya sendiri.
    # Menunggu di sini dulu hanya akan menunda window muncul tanpa manfaat,
    # dan justru inilah pola lama yang bisa membuat kiosk "terlihat blank"
    # kalau wait_ui() sempat timeout sebelum window dibuka sama sekali.
    if _pywebview_available():
        # Loop selamanya: open_pywebview() BLOCKING sampai window ditutup
        # (baik sengaja lewat tombol close/Alt+F4 peserta, maupun error).
        # Kalau peserta tidak sengaja menutup jendela, window otomatis
        # dibuka lagi dalam beberapa detik -- tidak perlu panitia/peserta
        # menjalankan apa pun secara manual. Hanya keluar dari loop kalau
        # open_pywebview() gagal TOTAL (pywebview/WebKit rusak), baru jatuh
        # ke fallback browser di bawah.
        while True:
            if not open_pywebview():
                print("[kiosk] pywebview gagal dibuka -- beralih ke mode browser.",
                      flush=True)
                break
            print("[kiosk] Window kiosk ditutup -- membuka lagi otomatis dalam 2 "
                  "detik (supaya peserta tidak kehilangan akses walau jendela "
                  "tidak sengaja tertutup)...", flush=True)
            time.sleep(2)
    # Fallback ke browser: tidak ada halaman loading kustom, jadi tunggu UI
    # dulu di sini supaya browser tidak membuka halaman connection-error.
    if not wait_ui():
        print("[kiosk] UI lokal tidak siap. Cek koneksi/konfigurasi agent.", flush=True)
    if not open_browser_kiosk():
        print("[kiosk] Tidak ada penampil tersedia. Buka manual: " + URL, flush=True)
        while True:
            time.sleep(3600)


def _cleanup(*_):
    stop_agent()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _cleanup)
    signal.signal(signal.SIGINT, _cleanup)
    try:
        main()
    finally:
        stop_agent()
