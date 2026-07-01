"""Check: SSH root login dinonaktifkan.

PASS bila /etc/ssh/sshd_config memiliki 'PermitRootLogin no' (efektif,
mengabaikan baris komentar) ATAU sshd memang tidak mengizinkan root.
"""
import os
import re

SSHD_CONFIG = "/etc/ssh/sshd_config"


def run(ctx=None):
    path = (ctx or {}).get("sshd_config", SSHD_CONFIG)
    if not os.path.isfile(path):
        return {"passed": False, "evidence": {"reason": "sshd_config tidak ditemukan"}}

    effective = None  # nilai PermitRootLogin terakhir yang tidak dikomentari
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                m = re.match(r"(?i)^PermitRootLogin\s+(\S+)", s)
                if m:
                    effective = m.group(1).lower()
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}

    passed = (effective == "no")
    return {
        "passed": passed,
        "evidence": {"permit_root_login": effective if effective is not None else "default(unset)"},
    }
