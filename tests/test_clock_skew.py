"""Unit test untuk perbaikan clock-skew (REVIEW-DAN-KONSEP-v2.md §2.1).

Skenario yang diuji: jam VM peserta MELESET (mis. VM clone/template VMware
tanpa NTP), tapi agen tetap harus menghasilkan timestamp yang lolos jendela
toleransi ±5 menit di server (lihat web/lib/hmac.ts) begitu clock_offset_ms
sudah diketahui — TANPA perlu refresh jam Ubuntu/VMware secara manual.

Jalankan: cd tests && python3 -m pytest -q
"""
import os
import sys
import time
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))

import crypto.signing as signing  # noqa: E402
from crypto.signing import build_auth_headers  # noqa: E402

TS_WINDOW_MS = 5 * 60 * 1000  # sama dengan web/lib/hmac.ts


def _server_style_check(headers, server_now_ms):
    """Meniru validasi server (lib/hmac.ts): |server_now - X-Timestamp| <= window."""
    ts = int(headers["X-Timestamp"])
    return abs(server_now_ms - ts) <= TS_WINDOW_MS


def test_signing_without_offset_fails_when_clock_is_skewed():
    """Tanpa koreksi (offset=0), VM yang jamnya meleset 30 menit menghasilkan
    timestamp yang DITOLAK server — inilah bug lama (poin/timestamp macet)."""
    real_now_ms = time.time() * 1000
    skewed_local_now_ms = real_now_ms - 30 * 60 * 1000  # VM mundur 30 menit

    with mock.patch.object(signing.time, "time", return_value=skewed_local_now_ms / 1000):
        headers = build_auth_headers("p1", "secret", "GET", "/api/v1/state", "",
                                     clock_offset_ms=0)

    assert not _server_style_check(headers, real_now_ms), (
        "seharusnya GAGAL tanpa koreksi offset — kalau lolos berarti skenario tes salah"
    )


def test_signing_with_offset_corrects_skewed_clock():
    """Dengan clock_offset_ms hasil sync_clock() (offset = server_time - local_time),
    timestamp yang dikirim harus lolos jendela toleransi server walau jam VM
    meleset jauh. Ini inti perbaikan REVIEW-DAN-KONSEP-v2.md §2.1."""
    real_now_ms = time.time() * 1000
    skew_ms = -30 * 60 * 1000  # VM mundur 30 menit
    skewed_local_now_ms = real_now_ms + skew_ms
    offset_ms = -skew_ms  # persis yang dihitung ApiClient.sync_clock()

    with mock.patch.object(signing.time, "time", return_value=skewed_local_now_ms / 1000):
        headers = build_auth_headers("p1", "secret", "GET", "/api/v1/state", "",
                                     clock_offset_ms=offset_ms)

    assert _server_style_check(headers, real_now_ms), (
        "timestamp masih di luar jendela toleransi server meski offset sudah diberikan"
    )


def test_large_skew_rejected_by_server_style_window():
    """Sanity check: validator ala-server memang menolak skew besar bila TIDAK
    dikoreksi — membuktikan diagnosis akar masalah (bukan cuma UI yang salah)."""
    real_now_ms = time.time() * 1000
    skewed_local_now_ms = real_now_ms - 30 * 60 * 1000

    with mock.patch.object(signing.time, "time", return_value=skewed_local_now_ms / 1000):
        headers = build_auth_headers("p1", "secret", "GET", "/api/v1/state", "",
                                     clock_offset_ms=0)

    assert not _server_style_check(headers, real_now_ms)
