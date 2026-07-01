"""Network Client (TDD §16, §17).

Tanggung jawab:
- Panggil endpoint /v1 (register, state, score, snapshot, heartbeat).
- Sertakan header signing HMAC untuk endpoint agen.
- Retry + exponential backoff + jitter pada kegagalan jaringan/5xx.
- Store-and-forward: skor/snapshot saat OFFLINE diantre & dikirim ulang (idempoten).
"""
import json
import random
import time

import requests

from crypto import build_auth_headers

BACKOFF_SCHEDULE = [5, 10, 20, 40, 60]  # detik (TDD §17.2)


class ApiClient:
    def __init__(self, base_url, logger, timeout=15):
        self.base = base_url.rstrip("/")
        self.log = logger
        self.timeout = timeout
        self.participant_id = None
        self.secret = None
        self._queue = []  # store-and-forward: list of (path, payload)

    def set_credentials(self, participant_id, secret):
        self.participant_id = participant_id
        self.secret = secret

    # ---------- low-level ----------
    def _post(self, path, payload, signed=True):
        url = self.base + path
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        headers = {"Content-Type": "application/json"}
        if signed and self.participant_id and self.secret:
            headers = build_auth_headers(self.participant_id, self.secret, "POST", path, body)
        resp = requests.post(url, data=body.encode("utf-8"), headers=headers, timeout=self.timeout)
        return resp

    def _get(self, path, signed=True):
        url = self.base + path
        headers = {}
        if signed and self.participant_id and self.secret:
            headers = build_auth_headers(self.participant_id, self.secret, "GET", path, "")
        resp = requests.get(url, headers=headers, timeout=self.timeout)
        return resp

    # ---------- endpoints ----------
    def register(self, name, school, session_code, image_version):
        payload = {"name": name, "school": school,
                   "session_code": session_code, "image_version": image_version}
        resp = self._post("/api/v1/register", payload, signed=False)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"register gagal: {resp.status_code} {resp.text[:200]}")

    def get_state(self):
        """Return dict state atau None bila gagal (caller anggap OFFLINE)."""
        try:
            resp = self._get("/api/v1/state")
            if resp.status_code == 200:
                return resp.json()
            self.log.warn("state_non200", code=resp.status_code)
        except requests.RequestException as e:
            self.log.warn("state_network_error", error=str(e))
        return None

    def send_heartbeat(self, agent_version, uptime_s):
        try:
            self._post("/api/v1/heartbeat",
                       {"agent_version": agent_version, "uptime_s": uptime_s})
        except requests.RequestException:
            pass

    def send_score(self, total_score, checks, computed_at_ms):
        payload = {"total_score": total_score, "checks": checks,
                   "computed_at_ms": computed_at_ms}
        return self._enqueue_and_flush("/api/v1/score", payload)

    def send_snapshot(self, snapshot):
        return self._enqueue_and_flush("/api/v1/snapshot", snapshot)

    # ---------- store-and-forward ----------
    def _enqueue_and_flush(self, path, payload):
        self._queue.append((path, payload))
        return self.flush_queue()

    def flush_queue(self):
        """Kirim semua item antrian. Yang gagal tetap di antrian (retry nanti)."""
        remaining = []
        ok = True
        for path, payload in self._queue:
            try:
                resp = self._post(path, payload)
                if resp.status_code in (200, 409):
                    # 409 = sesi ended/duplikat: anggap selesai (idempoten), buang
                    continue
                if resp.status_code == 429:
                    self.log.warn("rate_limited", path=path)
                    remaining.append((path, payload))
                    ok = False
                elif 500 <= resp.status_code < 600:
                    remaining.append((path, payload))
                    ok = False
                else:
                    # 4xx lain: payload bermasalah, jangan ulang membabi buta
                    self.log.error("post_4xx", path=path, code=resp.status_code)
            except requests.RequestException as e:
                self.log.warn("post_network_error", path=path, error=str(e))
                remaining.append((path, payload))
                ok = False
        self._queue = remaining
        return ok

    def backoff_sleep(self, attempt):
        base = BACKOFF_SCHEDULE[min(attempt, len(BACKOFF_SCHEDULE) - 1)]
        jitter = base * 0.2 * (random.random() * 2 - 1)  # ±20%
        time.sleep(max(1, base + jitter))
