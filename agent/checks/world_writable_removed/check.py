"""Check: file sentinel tidak world-writable.

PASS bila /opt/dhc/secret.txt tidak dapat ditulis 'other' (atau file tidak ada).
"""
import os, stat

def run(ctx=None):
    path = (ctx or {}).get("wwf_path", "/opt/dhc/secret.txt")
    try:
        if not os.path.exists(path):
            return {"passed": True, "evidence": {"note": "file tidak ada"}}
        perm = stat.S_IMODE(os.stat(path).st_mode)
        other_write = perm & 0o002
        return {"passed": other_write == 0, "evidence": {"mode": oct(perm)}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
