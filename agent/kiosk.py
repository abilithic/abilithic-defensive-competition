#!/usr/bin/env python3
"""abilithic DHC — Kiosk launcher.

Menjalankan agent (main.py) di latar, menunggu UI lokal siap, lalu membuka
UI itu sebagai **aplikasi fullscreen** — tanpa peserta perlu buka terminal/browser.

Urutan mode tampilan (pakai yang pertama tersedia):
  1) pywebview  -> jendela native app (paling "aplikasi", tanpa browser chrome)
  2) firefox --kiosk / chromium --app --kiosk / chrome --kiosk (fallback andal)

Jalankan: python3 kiosk.py   (biasanya dipanggil otomatis oleh autostart)
"""
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8080
URL = f"http://127.0.0.1:{PORT}"

_agent_proc = None


def start_agent():
    """Jalankan agent (main.py) sebagai proses terpisah."""
    global _agent_proc
    py = sys.executable or "python3"
    _agent_proc = subprocess.Popen([py, os.path.join(HERE, "main.py")])
    return _agent_proc


def wait_ui(timeout=40):
    """Tunggu sampai UI lokal merespons."""
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
    """Mode paling 'aplikasi'. Return True bila berhasil dibuka."""
    try:
        import webview  # pywebview
    except Exception:
        return False
    try:
        webview.create_window("abilithic DHC", URL, fullscreen=True,
                              background_color="#0a0e1a")
        webview.start()
        return True
    except Exception as e:
        print(f"[kiosk] pywebview gagal: {e}", flush=True)
        return False


def open_browser_kiosk():
    """Fallback: buka browser terpasang dalam mode kiosk/fullscreen."""
    candidates = [
        ["firefox", "--kiosk", URL],
        ["chromium-browser", f"--app={URL}", "--kiosk", "--start-fullscreen", "--no-first-run"],
        ["chromium", f"--app={URL}", "--kiosk", "--start-fullscreen", "--no-first-run"],
        ["google-chrome", f"--app={URL}", "--kiosk", "--no-first-run"],
        ["google-chrome-stable", f"--app={URL}", "--kiosk", "--no-first-run"],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            print(f"[kiosk] membuka via {cmd[0]}", flush=True)
            proc = subprocess.Popen(cmd)
            proc.wait()  # blok sampai browser ditutup
            return True
    # upaya terakhir
    if shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", URL])
        # tetap hidup agar agent jalan
        while True:
            time.sleep(3600)
    return False


def main():
    print("[kiosk] menjalankan agent...", flush=True)
    start_agent()

    if not wait_ui():
        print("[kiosk] UI lokal tidak siap. Cek koneksi/konfigurasi agent.", flush=True)

    # tampilkan sebagai aplikasi
    if not open_pywebview():
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
