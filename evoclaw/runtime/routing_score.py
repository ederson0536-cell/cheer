"""Routing score reference implementation.

Usage:
  python3 evoclaw/runtime/routing_score.py evoclaw/runtime/examples/skill_registry.example.json
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass

TRUST_MAP = {
    "unverified": 0.25,
    "low": 0.4,
    "medium": 0.7,
    "high": 1.0,
}


@dataclass
class Weights:
    w1: float = 0.20
    w2: float = 0.25
    w3: float = 0.15
    w4: float = 0.10
    w5: float = 0.15
    w6: float = 0.15


def score_skill(skill: dict, hard_constraint_pass: int = 1, w: Weights = Weights()) -> float:
    f = skill["routing_features"]
    trust_level = TRUST_MAP[skill["trust_level"]]

    score = hard_constraint_pass * (
        w.w1 * f["rule_alignment"]
        + w.w2 * f["success_rate"]
        - w.w3 * f["rework_rate"]
        - w.w4 * f["latency_penalty"]
        + w.w5 * trust_level
        + w.w6 * f["scenario_match"]
    )

    return max(0.0, min(1.0, round(score, 4)))


def band(score: float) -> str:
    if score > 0.75:
        return "auto_execute"
    if score >= 0.60:
        return "cautious_review_or_canary"
    return "reject_auto"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 routing_score.py <skill_registry.json>")
        return 1

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        payload = json.load(f)

    rows = []
    for skill in payload.get("skills", []):
        s = score_skill(skill)
        rows.append((skill["skill_id"], s, band(s)))

    rows.sort(key=lambda x: x[1], reverse=True)
    for skill_id, s, b in rows:
        print(f"{skill_id}\t{s}\t{b}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
