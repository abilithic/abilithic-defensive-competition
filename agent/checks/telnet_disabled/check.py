"""Check: Telnet dimatikan.

PASS bila tidak ada socket LISTEN di port 23 (TCP). Membaca /proc/net/tcp[6]
(tanpa dependensi eksternal). Port 23 = 0x17 dalam hex.
"""

LISTEN = "0A"  # status TCP_LISTEN di /proc/net/tcp
PORT_23_HEX = "0017"


def _has_listen_on(path, port_hex):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            next(f, None)  # header
            for line in f:
                parts = line.split()
                if len(parts) < 4:
                    continue
                local = parts[1]          # mis. 00000000:0017
                st = parts[3]
                if st == LISTEN and local.upper().endswith(":" + port_hex):
                    return True
    except FileNotFoundError:
        return False
    except Exception:
        return False
    return False


def run(ctx=None):
    listening = (_has_listen_on("/proc/net/tcp", PORT_23_HEX)
                 or _has_listen_on("/proc/net/tcp6", PORT_23_HEX))
    return {
        "passed": not listening,
        "evidence": {"telnet_port_23_listening": listening},
    }
