"""Scoring engine — PURE FUNCTION (TDD §14, §35).

Deterministik, tanpa efek samping, mudah diuji (lihat tests/test_score_engine.py).

Konsep:
- eligible(check): hanya check non-penalti yang GAGAL saat START boleh memberi poin.
  -> menutup celah "memperbaiki sebelum START" (pre-fix tidak menguntungkan).
- earned: points bila eligible DAN passed sekarang.
- penalty: untuk check must_stay_passing yang sekarang GAGAL -> -points * penalty_weight.

Format `checks` (list of dict):
  { "code", "points", "is_penalty"(bool), "must_stay_passing"(bool) }
`start_state` / `current_state`: dict code -> passed(bool).
"""
from typing import Dict, List


def compute_eligibility(checks: List[dict], start_state: Dict[str, bool]) -> Dict[str, bool]:
    """Tentukan check mana yang eligible diberi poin (gagal saat START)."""
    eligible = {}
    for c in checks:
        code = c["code"]
        if c.get("must_stay_passing"):
            # check ketersediaan: bukan tugas yang diskor positif
            eligible[code] = False
            continue
        # eligible jika saat START statusnya GAGAL (atau tak diketahui -> anggap gagal/tugas)
        eligible[code] = (start_state.get(code, False) is False)
    return eligible


def compute_score(checks: List[dict],
                  start_state: Dict[str, bool],
                  current_state: Dict[str, bool],
                  penalty_weight: float = 1.0) -> dict:
    """Hitung skor total + rincian per check.

    Return:
      {
        "total": int,
        "breakdown": [ {code, eligible, passed, earned, penalty}, ... ]
      }
    """
    eligibility = compute_eligibility(checks, start_state)
    total = 0
    breakdown = []

    for c in checks:
        code = c["code"]
        points = int(c.get("points", 0))
        passed_now = bool(current_state.get(code, False))
        eligible = eligibility.get(code, False)
        earned = 0
        penalty = 0

        if c.get("must_stay_passing"):
            # penalti bila layanan wajib mati sekarang
            if not passed_now:
                penalty = -int(round(points * penalty_weight))
        else:
            if eligible and passed_now:
                earned = points

        total += earned + penalty
        breakdown.append({
            "code": code,
            "eligible": eligible,
            "passed": passed_now,
            "earned": earned,
            "penalty": penalty,
        })

    return {"total": total, "breakdown": breakdown}
