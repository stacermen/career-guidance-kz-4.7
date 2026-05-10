"""Unit tests for the scoring service.

These tests are framework- and DB-free: they exercise the pure scoring
functions directly with hand-crafted answer dicts.
"""

from __future__ import annotations

import pytest

from app.services.scoring_service import (
    BIG_FIVE_DIMS,
    COGNITIVE_DIMS,
    HOLLAND_DIMS,
    MI_DIMS,
    VALUE_DIMS,
    holland_code_letters,
    score_all,
    score_big_five,
    score_cognitive,
    score_holland,
    score_multiple_intelligences,
    score_values,
)

# --------------------------- helpers ----------------------------------------


def _scale_answer(value: int, trait: str, *, reverse: bool = False, qtype: str = "scale") -> dict:
    return {
        "value": value,
        "question_type": qtype,
        "meta": {"trait": trait, "reverse": reverse},
    }


# --------------------------- Holland ----------------------------------------


def test_holland_all_max_yields_100() -> None:
    answers = [_scale_answer(5, d) for d in HOLLAND_DIMS for _ in range(7)]
    out = score_holland(answers)
    for d in HOLLAND_DIMS:
        assert out[d] == 100.0


def test_holland_all_min_yields_0() -> None:
    answers = [_scale_answer(1, d) for d in HOLLAND_DIMS for _ in range(7)]
    out = score_holland(answers)
    for d in HOLLAND_DIMS:
        assert out[d] == 0.0


def test_holland_reverse_flips_value() -> None:
    out = score_holland([_scale_answer(1, "R", reverse=True)])
    assert out["R"] == 100.0


def test_holland_code_letters_orders_descending() -> None:
    code = holland_code_letters({"R": 10, "I": 90, "A": 70, "S": 80, "E": 50, "C": 30})
    assert code == "ISA"


def test_holland_unknown_trait_is_ignored() -> None:
    out = score_holland([_scale_answer(5, "X")])
    assert all(v == 0.0 for v in out.values())


# --------------------------- Big Five ---------------------------------------


def test_big_five_balanced_input() -> None:
    answers = [_scale_answer(3, d) for d in BIG_FIVE_DIMS for _ in range(6)]
    out = score_big_five(answers)
    for d in BIG_FIVE_DIMS:
        assert out[d] == 50.0  # midpoint of 1..5 → 50%


def test_big_five_handles_reverse() -> None:
    out = score_big_five([_scale_answer(2, "N", reverse=True)])
    # 2 reversed → 4 → (4-1)/4 * 100 = 75
    assert out["N"] == 75.0


# --------------------------- Multiple Intelligences -------------------------


def test_mi_returns_all_dimensions() -> None:
    out = score_multiple_intelligences([])
    assert set(out.keys()) == set(MI_DIMS)
    assert all(v == 0.0 for v in out.values())


def test_mi_per_dimension() -> None:
    answers = [_scale_answer(4, "logical") for _ in range(5)]
    out = score_multiple_intelligences(answers)
    assert out["logical"] == pytest.approx(75.0, abs=0.1)
    assert out["linguistic"] == 0.0


# --------------------------- Values -----------------------------------------


def test_values_likert_basic() -> None:
    answers = [
        {
            "value": 5,
            "question_type": "scale",
            "meta": {"trait": "creativity", "reverse": False},
        }
    ]
    out = score_values(answers)
    assert out["creativity"] == 100.0


def test_values_ranking_awards_top_first() -> None:
    answers = [
        {
            "value": ["autonomy", "creativity", "stability", "income", "social_impact", "prestige", "variety"],
            "question_type": "ranking",
            "meta": {},
        }
    ]
    out = score_values(answers)
    # Ranking-only path — every dim is touched, but autonomy should top variety.
    assert out["autonomy"] >= out["creativity"] >= out["stability"]
    assert out["autonomy"] > out["variety"]


def test_values_returns_all_dims() -> None:
    out = score_values([])
    assert set(out.keys()) == set(VALUE_DIMS)


# --------------------------- Cognitive --------------------------------------


def test_cognitive_basic() -> None:
    answers = [
        _scale_answer(5, "analytical"),
        _scale_answer(5, "analytical"),
        _scale_answer(1, "intuitive"),
        _scale_answer(5, "detail"),
        _scale_answer(3, "big_picture"),
    ]
    out = score_cognitive(answers)
    assert out["analytical"] == 100.0
    assert out["intuitive"] == 0.0
    assert out["detail"] == 100.0
    assert out["big_picture"] == 50.0


def test_cognitive_returns_all_dims() -> None:
    out = score_cognitive([])
    assert set(out.keys()) == set(COGNITIVE_DIMS)


# --------------------------- Aggregate --------------------------------------


def test_score_all_handles_empty_groups() -> None:
    out = score_all({})
    for k in ("holland", "big_five", "mi", "values", "cognitive"):
        assert k in out
        for v in out[k].values():
            assert v == 0.0
