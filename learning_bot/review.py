from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from difflib import SequenceMatcher


@dataclass(frozen=True)
class ReviewState:
    repetitions: int = 0
    interval_days: int = 0
    ease_factor: float = 2.5


@dataclass(frozen=True)
class ReviewUpdate:
    repetitions: int
    interval_days: int
    ease_factor: float
    due_at: datetime


def schedule_sm2(state: ReviewState, quality: int, now: datetime | None = None) -> ReviewUpdate:
    if quality not in range(6):
        raise ValueError("quality must be between 0 and 5")
    now = now or datetime.now(UTC)
    ease = max(1.3, state.ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if quality < 3:
        repetitions, interval = 0, 1
    else:
        repetitions = state.repetitions + 1
        if repetitions == 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval = max(1, round(state.interval_days * ease))
    return ReviewUpdate(repetitions, interval, ease, now + timedelta(days=interval))


def normalize_answer(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return " ".join("".join(ch for ch in normalized if ch.isalnum() or ch.isspace()).split())


def answers_match(actual: str, expected: str, threshold: float = 0.86) -> bool:
    left, right = normalize_answer(actual), normalize_answer(expected)
    return bool(left and right) and (left == right or SequenceMatcher(None, left, right).ratio() >= threshold)

