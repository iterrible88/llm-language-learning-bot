# LLM Language Learning Bot

A privacy-safe portfolio edition of a Telegram learning assistant. It generates structured lessons for any user-selected language pair, validates model output, stores progress in SQLite, and schedules vocabulary review with SM-2 spaced repetition.

The repository focuses on reliable LLM product engineering rather than a one-off chat completion: typed contracts, provider abstraction, deterministic fallback, persistent state and testable learning logic.

> No production token, chat history, personal profile, original database or provider-specific credential is included.

## Features

- Telegram workflow built with Aiogram 3 and FSM.
- Per-user native language, target language, level and interests.
- LLM-generated lessons returned through a strict JSON contract.
- Pydantic validation and normalization of model output.
- OpenAI-compatible HTTP adapter plus an offline mock provider.
- SQLite repository for profiles, lessons, vocabulary and reviews.
- SM-2 spaced repetition with due-date scheduling.
- Tolerant answer comparison using Unicode normalization and similarity.
- Provider-independent service layer that can be tested without Telegram.
- Runnable CLI demonstration and automated unit tests.

## Architecture

```text
Telegram / CLI
    -> LearningService
        -> PromptFactory
        -> LLMProvider
            -> MockProvider
            -> OpenAICompatibleProvider
        -> Pydantic lesson contract
        -> SQLiteRepository
        -> SM-2 review scheduler
```

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
python -m scripts.demo
```

To run Telegram polling, copy `.env.example` to `.env`, supply your token and environment variables, then run:

```bash
python -m learning_bot.bot
```

The default `mock` provider makes the service and demo work without a paid LLM API. To connect an OpenAI-compatible endpoint, set `LLM_PROVIDER=http`, its base URL, key and model.

## Bot commands

- `/start` — create a profile and show help;
- `/profile` — configure the language pair and level;
- `/lesson` — generate and save a structured lesson;
- `/review` — review due vocabulary;
- `/progress` — show learning statistics.

## Reliability choices

- LLM output is treated as untrusted input and validated before persistence.
- The service requests JSON only and extracts fenced JSON defensively.
- Database writes use transactions and foreign keys.
- Learning logic is isolated from Telegram handlers.
- The mock provider provides deterministic offline tests.

See [architecture notes](docs/architecture.md) and [security notes](SECURITY.md).

