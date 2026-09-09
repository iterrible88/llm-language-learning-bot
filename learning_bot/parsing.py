from __future__ import annotations

import json

from learning_bot.models import Lesson


def parse_lesson(text: str) -> Lesson:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    start, end = candidate.find("{"), candidate.rfind("}")
    if start < 0 or end < start:
        raise ValueError("LLM response does not contain a JSON object")
    payload = json.loads(candidate[start : end + 1])
    return Lesson.model_validate(payload)

