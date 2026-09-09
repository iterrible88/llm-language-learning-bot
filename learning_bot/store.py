from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from learning_bot.models import Lesson, UserProfile
from learning_bot.review import ReviewState, ReviewUpdate


class SQLiteRepository:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def _initialize(self) -> None:
        with closing(self._connect()) as db, db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY, native_language TEXT NOT NULL,
                    target_language TEXT NOT NULL, level TEXT NOT NULL, interests TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                    payload TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                    term TEXT NOT NULL, translation TEXT NOT NULL, example TEXT NOT NULL,
                    repetitions INTEGER NOT NULL DEFAULT 0, interval_days INTEGER NOT NULL DEFAULT 0,
                    ease_factor REAL NOT NULL DEFAULT 2.5, due_at TEXT NOT NULL,
                    UNIQUE(user_id, term),
                    FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
                );
                """
            )

    def save_profile(self, profile: UserProfile) -> None:
        with self._lock, closing(self._connect()) as db, db:
            db.execute(
                """INSERT INTO profiles VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET native_language=excluded.native_language,
                target_language=excluded.target_language, level=excluded.level, interests=excluded.interests""",
                (
                    profile.user_id, profile.native_language, profile.target_language,
                    profile.level, json.dumps(profile.interests, ensure_ascii=False),
                ),
            )

    def get_profile(self, user_id: int) -> UserProfile | None:
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["interests"] = json.loads(data["interests"])
        return UserProfile.model_validate(data)

    def save_lesson(self, user_id: int, lesson: Lesson) -> int:
        now = datetime.now(UTC).isoformat()
        with self._lock, closing(self._connect()) as db, db:
            cursor = db.execute(
                "INSERT INTO lessons(user_id, payload, created_at) VALUES (?, ?, ?)",
                (user_id, lesson.model_dump_json(), now),
            )
            for item in lesson.vocabulary:
                db.execute(
                    """INSERT INTO vocabulary(user_id, term, translation, example, due_at)
                    VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id, term) DO UPDATE SET
                    translation=excluded.translation, example=excluded.example""",
                    (user_id, item.term, item.translation, item.example, now),
                )
            return int(cursor.lastrowid)

    def due_vocabulary(self, user_id: int, limit: int = 10) -> list[dict]:
        with closing(self._connect()) as db:
            rows = db.execute(
                "SELECT * FROM vocabulary WHERE user_id = ? AND due_at <= ? ORDER BY due_at LIMIT ?",
                (user_id, datetime.now(UTC).isoformat(), limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def update_review(self, item_id: int, update: ReviewUpdate) -> None:
        with self._lock, closing(self._connect()) as db, db:
            db.execute(
                """UPDATE vocabulary SET repetitions=?, interval_days=?, ease_factor=?, due_at=?
                WHERE id=?""",
                (
                    update.repetitions, update.interval_days, update.ease_factor,
                    update.due_at.isoformat(), item_id,
                ),
            )

    def progress(self, user_id: int) -> dict[str, int]:
        with closing(self._connect()) as db:
            lessons = db.execute("SELECT COUNT(*) FROM lessons WHERE user_id=?", (user_id,)).fetchone()[0]
            words = db.execute("SELECT COUNT(*) FROM vocabulary WHERE user_id=?", (user_id,)).fetchone()[0]
        return {"lessons": lessons, "vocabulary": words}

