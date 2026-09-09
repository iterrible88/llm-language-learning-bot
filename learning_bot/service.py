from __future__ import annotations

from learning_bot.models import Lesson, UserProfile
from learning_bot.parsing import parse_lesson
from learning_bot.prompts import PromptFactory
from learning_bot.providers import LLMProvider
from learning_bot.store import SQLiteRepository


class LearningService:
    def __init__(self, repository: SQLiteRepository, provider: LLMProvider):
        self.repository = repository
        self.provider = provider
        self.prompts = PromptFactory()

    async def create_lesson(self, user_id: int) -> tuple[int, Lesson]:
        profile = self.repository.get_profile(user_id)
        if not profile:
            raise LookupError("User profile is not configured")
        raw = await self.provider.complete_json(self.prompts.lesson(profile))
        lesson = parse_lesson(raw)
        lesson_id = self.repository.save_lesson(user_id, lesson)
        return lesson_id, lesson

