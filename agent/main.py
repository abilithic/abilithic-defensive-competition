#!/usr/bin/env python3
"""abilithic-agent — entrypoint (TDD §8, §35).

Mengorkestrasi modul: StateManager, CheckRunner, ScoreEngine, ApiClient,
SnapshotManager, Logger, dan Local UI (Flask). Pola: agen POLLING ke server.

Jalankan (di dalam VM Ubuntu, butuh root agar bisa baca /etc/shadow dll):
    sudo python3 main.py
Lalu buka http://localhost:8080 untuk registrasi.
"""
import json
import os
import sys
import threading
import time

import yaml

# pastikan modul lokal bisa diimport saat dijalankan langsung
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import get_logger, set_level
from engine import StateManager, AgentState, compute_score
from runner import CheckRunner
from snapshot import SnapshotManager
from network import ApiClient
from ui import create_ui

AGENT_VERSION = "0.1.0"


def load_config():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "config.yaml")
    if not os.path.isfile(path):
        path = os.path.join(here, "config.example.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class Runtime:
    """State bersama antara loop polling dan Local UI."""

    def __init__(self, cfg, log):
        self.cfg = cfg
        self.log = log
        self.lock = threading.Lock()
        self.started = time.time()

        self.api = ApiClient(cfg["portal_url"], log)
        self.state_mgr = StateManager(log)
        self.runner = CheckRunner(log)
        self.snap = SnapshotManager(log)

        # data registrasi & sesi
        self.registered = False
        self.participant_id = None
        self.competition_id = None
        self.name = None
        self.school = None

        # data state lomba terkini (dari server)
        self.server_status = "waiting"
        self.active_codes = []
        self.hint_policy = "full"
        self.difficulty = "easy"
        self.ends_at_ms = None
        self.penalty_weight = 1.0

        # scoring
        self.start_state = {}     # baseline saat START (code -> passed)
        self.current_state = {}
        self.score = 0
        self.breakdown = []

        # koneksi
        self.conn = "connecting"  # connecting | ok | error
        self.last_sync = None     # epoch detik poll sukses terakhir
        self.fail_attempt = 0
        self._sync_lock = threading.Lock()  # cegah sync bersamaan (loop vs tombol)

    # ---------- dipanggil dari UI ----------
    def do_register(self, name, school, session_code):
        try:
            res = self.api.register(name, school, session_code, self.cfg["image_version"])
        except Exception as e:
            self.log.error("register_failed", error=str(e))
            return False, f"Registrasi gagal: {e}"
        with self.lock:
            self.participant_id = res["participant_id"]
            self.competition_id = res.get("competition_id")
            self.name, self.school = name, school
            self.registered = True
            self.api.set_credentials(res["participant_id"], res["agent_secret"])
            self.state_mgr.mark_registered()
        self.log.info("registered", participant_id=self.participant_id)
        # snapshot fase registration di BACKGROUND agar UI langsung merespons
        threading.Thread(target=self._safe_snapshot, args=("registration",),
                         daemon=True).start()
        return True, "Berhasil terdaftar. Menunggu START dari panitia..."

    def _safe_snapshot(self, phase):
        try:
            self._capture_and_send_snapshot(phase)
        except Exception as e:
            self.log.error("snapshot_failed", phase=phase, error=str(e))

    def _now_ms(self):
        """Waktu 'sekarang' terkoreksi offset jam server — dipakai utk timer/
        last_sync agar tetap akurat walau jam sistem VM ngaco (TDD clock-skew)."""
        return time.time() * 1000 + self.api.clock_offset_ms

    def status_snapshot(self):
        with self.lock:
            remaining = None
            if self.ends_at_ms and self.server_status == "running":
                remaining = max(0, int((self.ends_at_ms - self._now_ms()) / 1000))
            checks = []
            hints = self.runner.hints(self.active_codes, self.hint_policy)
            bd = {b["code"]: b for b in self.breakdown}
            for code in self.active_codes:
                c = self.runner.checks.get(code)
                checks.append({
                    "code": code,
                    "title": hints.get(code, {}).get("title", code),
                    "passed": self.current_state.get(code, False),
                    "hint": hints.get(code, {}).get("hint"),
                    "points": c.points if c else 10,
                })
            # catatan: last_sync_sec = selisih waktu LOKAL murni (elapsed), sengaja
            # TIDAK pakai _now_ms() terkoreksi — mengukur durasi berlalu tidak
            # butuh koreksi offset absolut, cukup jam lokal berjalan normal.
            last_sync_sec = int(time.time() - self.last_sync) if self.last_sync else None
            return {
                "registered": self.registered,
                "name": self.name, "school": self.school,
                "state": self.state_mgr.state.value,
                "score": self.score,
                "remaining_sec": remaining,
                "checks": checks,
                "connection": self.conn,          # connecting | ok | error
                "last_sync_sec": last_sync_sec,    # berapa detik lalu poll sukses
            }

    def sync_once(self):
        """Satu siklus: poll state -> terapkan -> scoring. Dipakai loop & tombol refresh.
        Return True bila poll sukses."""
        if not self.registered:
            return False
        with self._sync_lock:
            # Selalu sinkronkan jam LEBIH DULU (endpoint publik, tanpa signing).
            # Ini yang membuat proses berjalan otomatis walau jam VM ngaco —
            # tak perlu lagi refresh manual jam Ubuntu/VMware (lihat network/client.py).
            self.api.sync_clock()
            state = self.api.get_state()
            if state is None:
                self.state_mgr.mark_offline()
                self.conn = "error"
                self.fail_attempt += 1
                self.api.flush_queue()
                return False
            self.fail_attempt = 0
            self.conn = "ok"
            self.last_sync = time.time()

            with self.lock:
                self.server_status = state.get("status", "waiting")
                self.active_codes = state.get("active_check_codes", []) or self.active_codes
                self.hint_policy = state.get("hint_policy", self.hint_policy)
                self.difficulty = state.get("difficulty", self.difficulty)
                self.ends_at_ms = state.get("ends_at_ms", self.ends_at_ms)
                self.penalty_weight = float(state.get("penalty_weight", self.penalty_weight))
            self.state_mgr.apply_server_status(self.server_status)
            self.api.send_heartbeat(AGENT_VERSION, int(time.time() - self.started))

            if self.state_mgr.should_capture_start():
                self._safe_snapshot("start")

            if self.state_mgr.is_scoring():
                meta = self.runner.active_checks_meta(self.active_codes)
                cur, _ev = self.runner.run_active(self.active_codes)
                result = compute_score(meta, self.start_state, cur, self.penalty_weight)
                with self.lock:
                    self.current_state = cur
                    self.score = result["total"]
                    self.breakdown = result["breakdown"]
                payload = [{"code": b["code"], "passed": b["passed"]} for b in result["breakdown"]]
                self.api.send_score(result["total"], payload, int(self._now_ms()))
                self.log.info("score_sent", score=result["total"])

            if self.state_mgr.should_capture_stop():
                self._safe_snapshot("stop")
                self.log.info("competition_ended_frozen", final_score=self.score)
            return True

    # ---------- helper ----------
    def _capture_and_send_snapshot(self, phase):
        with self.lock:
            if not self.participant_id:
                return
            # jalankan check aktif (atau semua bila belum tahu) untuk merekam status
            codes = self.active_codes or list(self.runner.checks.keys())
            state, _ev = self.runner.run_active(codes)
            snap = self.snap.build(self.participant_id, self.competition_id, phase,
                                   state, self.cfg["image_version"], self.difficulty,
                                   now_ms=self._now_ms())
        self.api.send_snapshot(snap)
        if phase == "start":
            with self.lock:
                self.start_state = state
        self.log.info("snapshot_sent", phase=phase)


def main():
    cfg = load_config()
    set_level(cfg.get("log_level", "INFO"))
    log = get_logger("agent")
    log.info("agent_boot", version=AGENT_VERSION, portal=cfg["portal_url"])

    rt = Runtime(cfg, log)

    # jalankan Local UI di thread terpisah
    ui_app = create_ui(rt)
    ui_thread = threading.Thread(
        target=lambda: ui_app.run(host="127.0.0.1", port=cfg.get("local_ui_port", 8080),
                                  debug=False, use_reloader=False),
        daemon=True)
    ui_thread.start()
    log.info("local_ui_started", port=cfg.get("local_ui_port", 8080))

    poll_interval = cfg.get("poll_interval_sec", 15)

    # ---------- LOOP UTAMA ----------
    while True:
        if not rt.registered:
            time.sleep(2)
            continue
        ok = rt.sync_once()
        if not ok:
            rt.api.backoff_sleep(rt.fail_attempt)
            continue
        # interval adaptif: lebih rapat saat running, longgar saat menunggu
        sleep_for = poll_interval if rt.server_status == "running" else max(poll_interval, 20)
        time.sleep(sleep_for)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nagent dihentikan.")
