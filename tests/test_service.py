import asyncio
from pathlib import Path

from learning_bot.models import UserProfile
from learning_bot.providers import MockProvider
from learning_bot.service import LearningService
from learning_bot.store import SQLiteRepository


def test_service_persists_lesson_and_vocabulary(tmp_path: Path):
    repository = SQLiteRepository(tmp_path / "test.sqlite3")
    repository.save_profile(UserProfile(user_id=42, native_language="Source", target_language="Target"))
    lesson_id, _ = asyncio.run(LearningService(repository, MockProvider()).create_lesson(42))
    assert lesson_id == 1
    assert repository.progress(42) == {"lessons": 1, "vocabulary": 5}
    assert len(repository.due_vocabulary(42)) == 5
