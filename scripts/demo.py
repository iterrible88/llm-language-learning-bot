from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from learning_bot.models import UserProfile
from learning_bot.providers import MockProvider
from learning_bot.service import LearningService
from learning_bot.store import SQLiteRepository


async def run() -> None:
    with tempfile.TemporaryDirectory() as directory:
        repository = SQLiteRepository(Path(directory) / "demo.sqlite3")
        repository.save_profile(
            UserProfile(
                user_id=1,
                native_language="Language A",
                target_language="Language B",
                level="beginner",
                interests=["travel", "technology"],
            )
        )
        lesson_id, lesson = await LearningService(repository, MockProvider()).create_lesson(1)
        assert len(lesson.vocabulary) >= 3
        assert repository.progress(1) == {"lessons": 1, "vocabulary": 5}
        print(f"Demo completed: lesson={lesson_id}, vocabulary={len(lesson.vocabulary)}")


if __name__ == "__main__":
    asyncio.run(run())

