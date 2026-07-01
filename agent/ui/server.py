"""Local UI (TDD §8, §35) — Flask app di localhost:8080.

Halaman registrasi peserta + status/hint/timer realtime (polling JS ke /status).
Tidak menyentuh internet; hanya bicara ke 'runtime' (objek di main.py).
"""
import os

from flask import Flask, jsonify, render_template, request


def create_ui(runtime):
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), "templates"))

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json(force=True, silent=True) or {}
        name = (data.get("name") or "").strip()
        school = (data.get("school") or "").strip()
        code = (data.get("session_code") or "").strip()
        if not name or not code:
            return jsonify({"ok": False, "error": "Nama dan kode sesi wajib diisi"}), 400
        ok, msg = runtime.do_register(name, school, code)
        return (jsonify({"ok": True, "message": msg}) if ok
                else jsonify({"ok": False, "error": msg}), 200 if ok else 400)

    @app.route("/status")
    def status():
        return jsonify(runtime.status_snapshot())

    @app.route("/refresh", methods=["POST"])
    def refresh():
        # paksa agent poll ke server SEKARANG (tanpa nunggu interval)
        ok = runtime.sync_once()
        return jsonify({"ok": ok, **runtime.status_snapshot()})

    return app
