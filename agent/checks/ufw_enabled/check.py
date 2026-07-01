"""Check: firewall UFW aktif.

PASS bila `ufw status` melaporkan "Status: active".
Fallback: baca /etc/ufw/ufw.conf (ENABLED=yes) bila perintah tak tersedia.
"""
import subprocess


def run(ctx=None):
    try:
        out = subprocess.run(
            ["ufw", "status"],
            capture_output=True, text=True, timeout=10
        )
        text = (out.stdout + out.stderr).lower()
        if "status: active" in text:
            return {"passed": True, "evidence": {"ufw": "active"}}
        if "status: inactive" in text:
            return {"passed": False, "evidence": {"ufw": "inactive"}}
    except FileNotFoundError:
        pass
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}

    # Fallback baca file konfigurasi
    try:
        with open("/etc/ufw/ufw.conf", "r", encoding="utf-8", errors="ignore") as f:
            conf = f.read().lower()
        enabled = "enabled=yes" in conf.replace(" ", "")
        return {"passed": enabled, "evidence": {"ufw_conf_enabled": enabled}}
    except Exception:
        return {"passed": False, "evidence": {"ufw": "unknown"}}
