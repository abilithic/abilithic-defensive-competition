"""HMAC request signing (TDD §11.3).

v0.1 (MVP): tanda tangan HMAC-SHA256 atas (method + path + body + timestamp + nonce).
Server memverifikasi ulang dengan agent_secret yang dibagikan saat registrasi.
Nonce & timestamp disertakan sejak awal agar siap untuk replay-protection penuh
di fase produksi (TDD §37) tanpa mengubah kontrak.
"""
import hashlib
import hmac
import os
import time


def _canonical(method: str, path: str, body: str, timestamp: str, nonce: str) -> bytes:
    return f"{method.upper()}\n{path}\n{body}\n{timestamp}\n{nonce}".encode("utf-8")


def sign_payload(secret: str, method: str, path: str, body: str,
                 timestamp: str, nonce: str) -> str:
    msg = _canonical(method, path, body, timestamp, nonce)
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def build_auth_headers(participant_id: str, secret: str,
                       method: str, path: str, body: str) -> dict:
    """Header standar untuk endpoint agen ber-signing."""
    timestamp = str(int(time.time() * 1000))
    nonce = os.urandom(16).hex()
    signature = sign_payload(secret, method, path, body, timestamp, nonce)
    return {
        "X-Participant": participant_id,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }
