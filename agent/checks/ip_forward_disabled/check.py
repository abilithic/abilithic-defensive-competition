"""Check: IP forwarding mati. PASS bila /proc/sys/net/ipv4/ip_forward == 0."""
def run(ctx=None):
    path = (ctx or {}).get("ipf_path", "/proc/sys/net/ipv4/ip_forward")
    try:
        with open(path, "r") as f:
            val = f.read().strip()
        return {"passed": val == "0", "evidence": {"ip_forward": val}}
    except Exception as e:
        return {"passed": False, "evidence": {"error": str(e)}}
