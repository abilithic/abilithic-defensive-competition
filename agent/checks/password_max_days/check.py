"""Check: PASS_MAX_DAYS <= 365 di /etc/login.defs."""
import re

def run(ctx=None):
    path = (ctx or {}).get("login_defs", "/etc/login.defs")
    try:
        val = None
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if s.startswith("#"):
                    continue
                m = re.match(r"PASS_MAX_DAYS\s+(\d+)", s)
                if m:
                    val = int(m.group(1))
        passed = val is not None and val <= 365
        return {"passed": passed, "evidence": {"pass_max_days": val}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
