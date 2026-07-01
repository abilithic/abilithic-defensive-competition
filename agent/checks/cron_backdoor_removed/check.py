"""Check: cron backdoor hilang. PASS bila /etc/cron.d/dhc-backdoor tidak ada."""
import os

def run(ctx=None):
    path = (ctx or {}).get("cron_path", "/etc/cron.d/dhc-backdoor")
    exists = os.path.exists(path)
    return {"passed": not exists, "evidence": {"cron_backdoor_exists": exists}}
