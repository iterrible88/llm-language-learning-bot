from __future__ import annotations

import json

from learning_bot.models import UserProfile


class PromptFactory:
    def lesson(self, profile: UserProfile) -> list[dict[str, str]]:
        schema = {
            "title": "string",
            "objective": "string",
            "explanation": "string",
            "vocabulary": [{"term": "string", "translation": "string", "example": "string"}],
            "exercises": [
                {
                    "type": "translate|multiple_choice|fill_gap",
                    "question": "string",
                    "answer": "string",
                    "options": ["string"],
                    "hint": "string or null",
                }
            ],
        }
        interests = ", ".join(profile.interests) or "everyday communication"
        return [
            {
                "role": "system",
                "content": (
                    "You are a careful language tutor. Return only valid JSON. "
                    "Use age-neutral, safe examples. Never invent claims about the learner."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Create one {profile.level} lesson for learning {profile.target_language} "
                    f"through {profile.native_language}. Interests: {interests}. "
                    "Include 5-8 vocabulary entries and 3-5 exercises. "
                    f"Follow this exact shape: {json.dumps(schema, ensure_ascii=False)}"
                ),
            },
        ]

