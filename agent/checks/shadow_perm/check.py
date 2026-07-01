"""Check: permission /etc/shadow aman.

PASS bila /etc/shadow tidak memberi izin baca/tulis ke 'other' (world).
Aman: mode <= 0o640 pada bit 'other' = 0 (mis. 0640, 0600, 0000-ish).
"""
import os
import stat

SHADOW = "/etc/shadow"


def run(ctx=None):
    path = (ctx or {}).get("shadow_path", SHADOW)
    if not os.path.exists(path):
        return {"passed": False, "evidence": {"reason": "shadow tidak ditemukan"}}
    try:
        mode = os.stat(path).st_mode
        perm = stat.S_IMODE(mode)
        other_bits = perm & 0o007           # rwx untuk 'other'
        group_write = perm & 0o020          # tidak boleh group-writable
        passed = (other_bits == 0) and (group_write == 0)
        return {
            "passed": passed,
            "evidence": {"mode": oct(perm), "world_access": bool(other_bits)},
        }
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
