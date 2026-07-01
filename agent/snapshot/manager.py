"""Snapshot Manager (TDD §13 — Baseline & Evidence).

Mengambil snapshot di fase registration / start / stop:
- status semua check aktif (pass/fail)
- artefak forensik ringan (users, listening ports, file perms, config hashes)
- ditandatangani HMAC (server verifikasi + simpan append-only)
"""
import hashlib
import os
import time


def _sha256_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return "sha256:" + h.hexdigest()
    except Exception:
        return None


def _list_users():
    users = []
    try:
        with open("/etc/passwd", "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if ":" in line:
                    users.append(line.split(":", 1)[0])
    except Exception:
        pass
    return users


def _listening_ports():
    ports = set()
    for p in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                next(f, None)
                for line in f:
                    parts = line.split()
                    if len(parts) >= 4 and parts[3] == "0A":
                        hexport = parts[1].split(":")[-1]
                        try:
                            ports.add(int(hexport, 16))
                        except ValueError:
                            pass
        except Exception:
            continue
    return sorted(ports)


def _file_perm(path):
    try:
        import stat
        return oct(stat.S_IMODE(os.stat(path).st_mode))
    except Exception:
        return None


class SnapshotManager:
    def __init__(self, logger):
        self.log = logger

    def collect_artifacts(self):
        return {
            "users": _list_users(),
            "listening_ports": _listening_ports(),
            "file_perms": {"/etc/shadow": _file_perm("/etc/shadow")},
            "config_hashes": {"/etc/ssh/sshd_config": _sha256_file("/etc/ssh/sshd_config")},
        }

    def build(self, participant_id, competition_id, phase, checks_state,
              image_version, difficulty):
        """Bangun objek snapshot (belum ditandatangani)."""
        snap = {
            "schema_version": "1.0",
            "participant_id": participant_id,
            "competition_id": competition_id,
            "phase": phase,
            "taken_at_server_ms": int(time.time() * 1000),
            "image_version": image_version,
            "difficulty": difficulty,
            "checks_state": [
                {"code": c, "passed": bool(v)} for c, v in checks_state.items()
            ],
            "artifacts": self.collect_artifacts(),
        }
        self.log.info("snapshot_built", phase=phase, checks=len(checks_state))
        return snap
