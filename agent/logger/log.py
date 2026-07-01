"""Structured logger untuk abilithic-agent (TDD §21).

Level: DEBUG, INFO, WARN, ERROR (+ kategori AUDIT/SECURITY via param).
Output JSON satu baris agar mudah dibaca admin/forensik.
"""
import json
import sys
import time

_LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
_current_level = 20  # INFO


def set_level(level: str) -> None:
    global _current_level
    _current_level = _LEVELS.get(str(level).upper(), 20)


class _Logger:
    def __init__(self, name: str):
        self.name = name

    def _emit(self, level: str, event: str, **fields):
        if _LEVELS.get(level, 20) < _current_level:
            return
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level,
            "module": self.name,
            "event": event,
        }
        if fields:
            record["detail"] = fields
        sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def debug(self, event, **f): self._emit("DEBUG", event, **f)
    def info(self, event, **f): self._emit("INFO", event, **f)
    def warn(self, event, **f): self._emit("WARN", event, **f)
    def error(self, event, **f): self._emit("ERROR", event, **f)
    # AUDIT/SECURITY dikirim sebagai ERROR-level lokal + ditandai (server simpan event_logs)
    def security(self, event, **f): self._emit("ERROR", event, category="SECURITY", **f)


def get_logger(name: str) -> _Logger:
    return _Logger(name)
