# Architecture notes

## Separation of concerns

`LearningService` coordinates lesson generation and storage. `PromptFactory` defines the model contract. Provider adapters handle transport. `SQLiteRepository` persists state. `review.py` contains deterministic SM-2 scheduling, independent of both Telegram and the LLM.

## Lesson contract

The LLM must return a topic, explanation, vocabulary entries and exercises. Pydantic validates sizes, required fields and supported exercise types. Invalid model output fails explicitly rather than corrupting the learning state.

## Production path

The portfolio version uses SQLite and Telegram long polling. A larger deployment would add PostgreSQL, distributed scheduling, queue workers, observability, content moderation and provider-level retry/backoff. Those components are a scaling path, not a claim about this demo.

