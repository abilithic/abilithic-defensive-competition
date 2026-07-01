"""Check: SSH PermitEmptyPasswords no.

Default OpenSSH = no. PASS bila baris efektif != 'yes' (mengabaikan komentar).
"""
import os, re

def run(ctx=None):
    path = (ctx or {}).get("sshd_config", "/etc/ssh/sshd_config")
    if not os.path.isfile(path):
        return {"passed": False, "evidence": {"reason": "sshd_config tidak ada"}}
    effective = "no"  # default aman
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                m = re.match(r"(?i)^PermitEmptyPasswords\s+(\S+)", s)
                if m:
                    effective = m.group(1).lower()
        return {"passed": effective != "yes", "evidence": {"permit_empty_passwords": effective}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
