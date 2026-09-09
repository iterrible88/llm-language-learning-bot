import asyncio

from learning_bot.models import UserProfile
from learning_bot.parsing import parse_lesson
from learning_bot.prompts import PromptFactory
from learning_bot.providers import MockProvider


def test_mock_response_matches_lesson_contract():
    profile = UserProfile(user_id=1, native_language="Source", target_language="Target")
    raw = asyncio.run(MockProvider().complete_json(PromptFactory().lesson(profile)))
    lesson = parse_lesson(f"```json\n{raw}\n```")
    assert len(lesson.vocabulary) == 5
    assert len(lesson.exercises) == 3


def test_prompt_uses_configured_language_pair():
    profile = UserProfile(user_id=1, native_language="Source", target_language="Target")
    prompt = PromptFactory().lesson(profile)[1]["content"]
    assert "Target" in prompt and "Source" in prompt
