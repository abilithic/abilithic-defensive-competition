"""Check: hanya 'root' yang ber-UID 0. PASS bila akun UID 0 tepat {root}."""
def run(ctx=None):
    path = (ctx or {}).get("passwd_path", "/etc/passwd")
    try:
        uid0 = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                p = line.strip().split(":")
                if len(p) >= 3 and p[2] == "0":
                    uid0.append(p[0])
        passed = uid0 == ["root"] or (len(uid0) == 1 and uid0[0] == "root")
        return {"passed": passed, "evidence": {"uid0_accounts": uid0}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
