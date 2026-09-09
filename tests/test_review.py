from datetime import UTC, datetime

from learning_bot.review import ReviewState, answers_match, schedule_sm2


def test_sm2_advances_successful_review():
    update = schedule_sm2(ReviewState(), quality=5, now=datetime(2026, 1, 1, tzinfo=UTC))
    assert update.repetitions == 1
    assert update.interval_days == 1


def test_sm2_resets_failed_review():
    state = ReviewState(repetitions=4, interval_days=20, ease_factor=2.4)
    update = schedule_sm2(state, quality=1)
    assert update.repetitions == 0
    assert update.interval_days == 1


def test_answer_matching_normalizes_case_and_punctuation():
    assert answers_match("  Hello! ", "hello")

