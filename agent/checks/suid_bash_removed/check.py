"""Check: backdoor SUID shell hilang.

PASS bila /usr/local/bin/rootbash tidak ada, atau tidak ber-bit SUID.
"""
import os, stat

def run(ctx=None):
    path = (ctx or {}).get("suid_path", "/usr/local/bin/rootbash")
    try:
        if not os.path.exists(path):
            return {"passed": True, "evidence": {"note": "tidak ada"}}
        mode = os.stat(path).st_mode
        is_suid = bool(mode & stat.S_ISUID)
        return {"passed": not is_suid, "evidence": {"exists": True, "suid": is_suid}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
