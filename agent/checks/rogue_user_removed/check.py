"""Check: akun tak sah dihapus.

PASS bila user 'hacker' (rogue user yang ditanam) tidak ada di /etc/passwd.
Nama user rogue dapat dioverride via ctx['rogue_user'].
"""
import os

PASSWD = "/etc/passwd"
DEFAULT_ROGUE = "hacker"


def run(ctx=None):
    rogue = (ctx or {}).get("rogue_user", DEFAULT_ROGUE)
    path = (ctx or {}).get("passwd_path", PASSWD)
    if not os.path.isfile(path):
        return {"passed": False, "evidence": {"reason": "passwd tidak ditemukan"}}

    users = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if ":" in line:
                    users.append(line.split(":", 1)[0])
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}

    present = rogue in users
    return {
        "passed": not present,
        "evidence": {"rogue_user": rogue, "present": present},
    }
