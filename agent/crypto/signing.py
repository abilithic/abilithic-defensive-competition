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
                       method: str, path: str, body: str,
                       clock_offset_ms: int = 0) -> dict:
    """Header standar untuk endpoint agen ber-signing.

    `clock_offset_ms` mengoreksi jam lokal VM terhadap jam server (lihat
    ApiClient.sync_clock / GET /api/v1/time). Tanpa ini, VM dengan jam yang
    ngaco (umum pada VM hasil clone/template) akan gagal lolos jendela
    toleransi timestamp server (±5 menit) dan agen tampak "berhenti update"
    sampai jam VM dikoreksi manual.
    """
    timestamp = str(int(time.time() * 1000) + int(clock_offset_ms))
    nonce = os.urandom(16).hex()
    signature = sign_payload(secret, method, path, body, timestamp, nonce)
    return {
        "X-Participant": participant_id,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }
