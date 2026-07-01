"""Check: tidak ada akun dengan password kosong.

PASS bila tidak ada baris /etc/shadow yang field password-nya kosong ("").
Field '*' atau '!' (terkunci) dianggap aman.
"""
def run(ctx=None):
    path = (ctx or {}).get("shadow_path", "/etc/shadow")
    try:
        empty = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) >= 2 and parts[1] == "":
                    empty.append(parts[0])
        return {"passed": len(empty) == 0, "evidence": {"empty_password_users": empty}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
