from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    user_id: int
    native_language: str = Field(min_length=2, max_length=40)
    target_language: str = Field(min_length=2, max_length=40)
    level: Literal["beginner", "elementary", "intermediate", "advanced"] = "beginner"
    interests: list[str] = Field(default_factory=list, max_length=8)


class VocabularyItem(BaseModel):
    term: str = Field(min_length=1, max_length=120)
    translation: str = Field(min_length=1, max_length=200)
    example: str = Field(min_length=1, max_length=300)

    @field_validator("term", "translation", "example")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return " ".join(value.split())


class Exercise(BaseModel):
    type: Literal["translate", "multiple_choice", "fill_gap"]
    question: str = Field(min_length=3, max_length=400)
    answer: str = Field(min_length=1, max_length=200)
    options: list[str] = Field(default_factory=list, max_length=6)
    hint: str | None = Field(default=None, max_length=250)


class Lesson(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    objective: str = Field(min_length=5, max_length=300)
    explanation: str = Field(min_length=20, max_length=3000)
    vocabulary: list[VocabularyItem] = Field(min_length=3, max_length=12)
    exercises: list[Exercise] = Field(min_length=2, max_length=10)

