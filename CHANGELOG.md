# Changelog

Semua perubahan penting dicatat di sini. Format: [Keep a Changelog](https://keepachangelog.com),
versi mengikuti [SemVer](https://semver.org) (TDD §24).

## [Unreleased]

## [0.1.0] — 2026-06-30
### Added
- **Database**: schema Postgres (competitions, participants, checks, difficulties,
  participant_checks, scores, snapshots, event_logs, nonces) + view `leaderboard`.
- **Seed**: preset tingkat Easy/Medium/Hard + 5 check Linux dasar
  (ssh_root_disabled, ufw_enabled, telnet_disabled, rogue_user_removed, shadow_perm).
- **Agent (Python)**: arsitektur modular — state_manager, score_engine (pure fn),
  check_runner, network client + retry/backoff + store-and-forward, snapshot manager,
  crypto HMAC signing, logger terstruktur, local UI (localhost:8080).
- **Web (Next.js)**: API `/v1` (register, state, score, heartbeat, snapshot, admin),
  leaderboard realtime (Supabase Realtime), halaman admin START/PAUSE/STOP.
- **Baseline & Evidence**: snapshot registration/start/stop + eligibility anti pre-fix.
- **Governance**: README, LICENSE (MIT), CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, ADR-001..006.
- **CI**: GitHub Actions (lint + unit test scoring).

[Unreleased]: https://github.com/abilithic/abilithic-defensive-competition/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/abilithic/abilithic-defensive-competition/releases/tag/v0.1.0
