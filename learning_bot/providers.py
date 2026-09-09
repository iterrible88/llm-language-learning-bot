from __future__ import annotations

import json
from typing import Protocol

import httpx

from learning_bot.models import UserProfile


class LLMProvider(Protocol):
    async def complete_json(self, messages: list[dict[str, str]]) -> str: ...


class MockProvider:
    async def complete_json(self, messages: list[dict[str, str]]) -> str:
        return json.dumps(
            {
                "title": "Useful introductions",
                "objective": "Introduce yourself and ask a simple follow-up question.",
                "explanation": (
                    "Use the short expressions below to start a polite conversation. "
                    "Read each example aloud and then adapt it with your own details."
                ),
                "vocabulary": [
                    {"term": "hello", "translation": "greeting", "example": "Hello, nice to meet you."},
                    {"term": "name", "translation": "personal name", "example": "My name is Alex."},
                    {"term": "from", "translation": "place of origin", "example": "I am from my hometown."},
                    {"term": "work", "translation": "occupation", "example": "I work with technology."},
                    {"term": "learn", "translation": "gain knowledge", "example": "I learn every day."},
                ],
                "exercises": [
                    {"type": "translate", "question": "Write a greeting.", "answer": "hello", "options": []},
                    {
                        "type": "multiple_choice",
                        "question": "Which word describes gaining knowledge?",
                        "answer": "learn",
                        "options": ["work", "learn", "from"],
                    },
                    {"type": "fill_gap", "question": "My ___ is Alex.", "answer": "name", "options": []},
                ],
            },
            ensure_ascii=False,
        )


class OpenAICompatibleProvider:
    def __init__(self, base_url: str, api_key: str, model: str):
        if not api_key:
            raise ValueError("LLM_API_KEY is required for the HTTP provider")
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.model = model

    async def complete_json(self, messages: list[dict[str, str]]) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages, "temperature": 0.4},
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

