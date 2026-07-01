"""Check: /etc/passwd tidak writable oleh group/other. PASS bila mode <= 644."""
import os, stat

def run(ctx=None):
    path = (ctx or {}).get("passwd_path", "/etc/passwd")
    try:
        perm = stat.S_IMODE(os.stat(path).st_mode)
        writable_by_others = perm & 0o022  # group write | other write
        return {"passed": writable_by_others == 0, "evidence": {"mode": oct(perm)}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
