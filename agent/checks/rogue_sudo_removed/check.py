"""Check: user 'backdoor' tidak berada di grup sudo.

PASS bila 'backdoor' bukan anggota grup sudo (via /etc/group).
"""
def run(ctx=None):
    rogue = (ctx or {}).get("rogue_user", "backdoor")
    path = (ctx or {}).get("group_path", "/etc/group")
    try:
        members = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                p = line.strip().split(":")
                if len(p) >= 4 and p[0] == "sudo":
                    members = [m for m in p[3].split(",") if m]
        return {"passed": rogue not in members, "evidence": {"sudo_members": members}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
