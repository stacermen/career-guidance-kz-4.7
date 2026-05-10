"""Scoring algorithms for the five psychometric tests.

All scoring functions accept the list of *answered* questions (each with their
metadata) and return a dict whose keys are dimension names and whose values are
percentages (0–100). The metadata for each question is populated by the seed
script — see ``app/db/seed_data.py``.

Conventions
-----------
- Likert scales use 1..5 with optional reverse scoring (``reverse=True`` in meta).
- Choice questions return one of the option keys; the question metadata maps
  each option key to a dimension.
- Ranking questions return an ordered list of option keys; rank 1 awards the
  highest weight, rank N the lowest.

These functions are deliberately framework-free so they can be unit tested
without a database.
"""

from __future__ import annotations

from typing import Any

# --------------------------- Holland Code (RIASEC) -------------------------

HOLLAND_DIMS = ["R", "I", "A", "S", "E", "C"]


def score_holland(answers: list[dict[str, Any]]) -> dict[str, float]:
    """Compute RIASEC dimension scores as percentages of the maximum.

    Each question's metadata must contain ``trait`` (one of HOLLAND_DIMS).
    Likert values 1..5 contribute directly, with reverse-scoring honoured.
    """
    sums: dict[str, int] = dict.fromkeys(HOLLAND_DIMS, 0)
    counts: dict[str, int] = dict.fromkeys(HOLLAND_DIMS, 0)
    for a in answers:
        trait = a.get("meta", {}).get("trait")
        if trait not in HOLLAND_DIMS:
            continue
        v = int(a["value"])
        if a["meta"].get("reverse"):
            v = 6 - v
        sums[trait] += v
        counts[trait] += 1
    out: dict[str, float] = {}
    for d in HOLLAND_DIMS:
        if counts[d] == 0:
            out[d] = 0.0
        else:
            # 1..5 → 0..100, average per question
            out[d] = round(((sums[d] / counts[d]) - 1) / 4 * 100, 1)
    return out


def holland_code_letters(scores: dict[str, float]) -> str:
    """Return the standard 3-letter Holland Code (e.g. ``IAE``)."""
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return "".join(d for d, _ in ordered[:3])


# --------------------------- Big Five (BFI extended) ------------------------

BIG_FIVE_DIMS = ["O", "C", "E", "A", "N"]
BIG_FIVE_LABELS = {
    "O": "Открытость",
    "C": "Добросовестность",
    "E": "Экстраверсия",
    "A": "Доброжелательность",
    "N": "Нейротизм",
}


def score_big_five(answers: list[dict[str, Any]]) -> dict[str, float]:
    sums: dict[str, int] = dict.fromkeys(BIG_FIVE_DIMS, 0)
    counts: dict[str, int] = dict.fromkeys(BIG_FIVE_DIMS, 0)
    for a in answers:
        trait = a.get("meta", {}).get("trait")
        if trait not in BIG_FIVE_DIMS:
            continue
        v = int(a["value"])
        if a["meta"].get("reverse"):
            v = 6 - v
        sums[trait] += v
        counts[trait] += 1
    return {
        d: round(((sums[d] / counts[d]) - 1) / 4 * 100, 1) if counts[d] else 0.0
        for d in BIG_FIVE_DIMS
    }


# --------------------------- Multiple Intelligences -------------------------

MI_DIMS = [
    "linguistic",
    "logical",
    "spatial",
    "musical",
    "bodily",
    "interpersonal",
    "intrapersonal",
    "naturalistic",
]


def score_multiple_intelligences(answers: list[dict[str, Any]]) -> dict[str, float]:
    sums: dict[str, int] = dict.fromkeys(MI_DIMS, 0)
    counts: dict[str, int] = dict.fromkeys(MI_DIMS, 0)
    for a in answers:
        trait = a.get("meta", {}).get("trait")
        if trait not in MI_DIMS:
            continue
        v = int(a["value"])
        if a["meta"].get("reverse"):
            v = 6 - v
        sums[trait] += v
        counts[trait] += 1
    return {
        d: round(((sums[d] / counts[d]) - 1) / 4 * 100, 1) if counts[d] else 0.0
        for d in MI_DIMS
    }


# --------------------------- Work Values ------------------------------------

VALUE_DIMS = [
    "autonomy",
    "creativity",
    "stability",
    "income",
    "social_impact",
    "prestige",
    "variety",
]


def score_values(answers: list[dict[str, Any]]) -> dict[str, float]:
    """Most value items are Likert scaled; a small subset may be rankings.

    For rankings we award N points to rank 1, N-1 to rank 2, etc.
    """
    sums: dict[str, float] = dict.fromkeys(VALUE_DIMS, 0.0)
    counts: dict[str, float] = dict.fromkeys(VALUE_DIMS, 0.0)
    max_each: dict[str, float] = dict.fromkeys(VALUE_DIMS, 0.0)

    for a in answers:
        meta = a.get("meta") or {}
        qtype = a.get("question_type", "scale")
        if qtype == "scale":
            trait = meta.get("trait")
            if trait not in VALUE_DIMS:
                continue
            v = int(a["value"])
            if meta.get("reverse"):
                v = 6 - v
            sums[trait] += v
            counts[trait] += 1
            max_each[trait] += 5
        elif qtype == "ranking":
            ranking = a["value"]
            if not isinstance(ranking, list):
                continue
            n = len(ranking)
            for idx, key in enumerate(ranking):
                if key in VALUE_DIMS:
                    weight = n - idx  # rank 1 → highest
                    sums[key] += weight
                    counts[key] += 1
                    max_each[key] += n

    out: dict[str, float] = {}
    for d in VALUE_DIMS:
        if max_each[d] == 0:
            out[d] = 0.0
        else:
            # Normalize: actual / max → 0..100. Likert min is 1 (not 0); re-baseline:
            # for pure Likert min total = counts[d]*1 → subtract counts[d]
            min_each = counts[d] if counts[d] == max_each[d] / 5 else 0
            num = sums[d] - min_each
            den = max_each[d] - min_each
            out[d] = round(max(0.0, min(100.0, num / den * 100)), 1) if den > 0 else 0.0
    return out


# --------------------------- Cognitive Style --------------------------------

COGNITIVE_DIMS = ["analytical", "intuitive", "detail", "big_picture"]


def score_cognitive(answers: list[dict[str, Any]]) -> dict[str, float]:
    sums: dict[str, int] = dict.fromkeys(COGNITIVE_DIMS, 0)
    counts: dict[str, int] = dict.fromkeys(COGNITIVE_DIMS, 0)
    for a in answers:
        trait = a.get("meta", {}).get("trait")
        if trait not in COGNITIVE_DIMS:
            continue
        v = int(a["value"])
        if a["meta"].get("reverse"):
            v = 6 - v
        sums[trait] += v
        counts[trait] += 1
    return {
        d: round(((sums[d] / counts[d]) - 1) / 4 * 100, 1) if counts[d] else 0.0
        for d in COGNITIVE_DIMS
    }


# --------------------------- Aggregator -------------------------------------


def score_all(grouped: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, float]]:
    """Score every test module given answers grouped by test slug."""
    return {
        "holland": score_holland(grouped.get("holland", [])),
        "big_five": score_big_five(grouped.get("big_five", [])),
        "mi": score_multiple_intelligences(grouped.get("mi", [])),
        "values": score_values(grouped.get("values", [])),
        "cognitive": score_cognitive(grouped.get("cognitive", [])),
    }
