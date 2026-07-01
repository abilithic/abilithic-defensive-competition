"""Unit test untuk scoring engine (TDD §14, §25).

Scoring engine = pure function -> wajib 100% deterministik & tertutup test.
Jalankan: cd tests && python3 -m pytest -q   (atau: python3 test_score_engine.py)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))

from engine import compute_score, compute_eligibility  # noqa: E402

CHECKS = [
    {"code": "a", "points": 10, "must_stay_passing": False},
    {"code": "b", "points": 10, "must_stay_passing": False},
    {"code": "svc", "points": 10, "must_stay_passing": True},
]


def test_basic_fix_one_check():
    start = {"a": False, "b": False, "svc": True}
    cur = {"a": True, "b": False, "svc": True}
    assert compute_score(CHECKS, start, cur, 1.0)["total"] == 10


def test_prefix_not_scored():
    # b sudah lulus saat START -> tidak eligible -> tak memberi poin
    start = {"a": False, "b": True, "svc": True}
    cur = {"a": True, "b": True, "svc": True}
    r = compute_score(CHECKS, start, cur, 1.0)
    assert r["total"] == 10  # hanya 'a'
    bd = {x["code"]: x for x in r["breakdown"]}
    assert bd["b"]["eligible"] is False
    assert bd["b"]["earned"] == 0


def test_penalty_service_down():
    start = {"a": False, "b": False, "svc": True}
    cur = {"a": True, "b": True, "svc": False}   # svc mati
    r = compute_score(CHECKS, start, cur, 1.5)
    # 10 + 10 - (10*1.5) = 5
    assert r["total"] == 5


def test_all_fixed_full_score():
    start = {"a": False, "b": False, "svc": True}
    cur = {"a": True, "b": True, "svc": True}
    assert compute_score(CHECKS, start, cur, 1.0)["total"] == 20


def test_eligibility_excludes_penalty_checks():
    start = {"a": False, "b": False, "svc": True}
    elig = compute_eligibility(CHECKS, start)
    assert elig["a"] is True
    assert elig["b"] is True
    assert elig["svc"] is False  # must_stay_passing bukan tugas yang diskor positif


def test_nothing_done_zero():
    start = {"a": False, "b": False, "svc": True}
    cur = {"a": False, "b": False, "svc": True}
    assert compute_score(CHECKS, start, cur, 1.0)["total"] == 0


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                failed += 1; print(f"FAIL {name}: {e}")
    sys.exit(1 if failed else 0)
