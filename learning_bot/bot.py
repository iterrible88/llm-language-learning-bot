from __future__ import annotations

import asyncio
import html

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from learning_bot.config import Settings
from learning_bot.models import UserProfile
from learning_bot.providers import MockProvider, OpenAICompatibleProvider
from learning_bot.service import LearningService
from learning_bot.store import SQLiteRepository


class ProfileSetup(StatesGroup):
    native_language = State()
    target_language = State()
    level = State()


def create_router(service: LearningService, repository: SQLiteRepository) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer(
            "Welcome! Configure your language pair with /profile, then request /lesson. "
            "Use /review and /progress to continue learning."
        )

    @router.message(Command("profile"))
    async def profile(message: Message, state: FSMContext) -> None:
        await state.set_state(ProfileSetup.native_language)
        await message.answer("What language should explanations use?")

    @router.message(ProfileSetup.native_language)
    async def native_language(message: Message, state: FSMContext) -> None:
        await state.update_data(native_language=(message.text or "").strip())
        await state.set_state(ProfileSetup.target_language)
        await message.answer("What language do you want to learn?")

    @router.message(ProfileSetup.target_language)
    async def target_language(message: Message, state: FSMContext) -> None:
        await state.update_data(target_language=(message.text or "").strip())
        await state.set_state(ProfileSetup.level)
        await message.answer("Choose: beginner, elementary, intermediate, or advanced.")

    @router.message(ProfileSetup.level)
    async def level(message: Message, state: FSMContext) -> None:
        selected = (message.text or "").strip().lower()
        if selected not in {"beginner", "elementary", "intermediate", "advanced"}:
            await message.answer("Please choose one of the listed levels.")
            return
        data = await state.get_data()
        repository.save_profile(
            UserProfile(
                user_id=message.from_user.id,
                native_language=data["native_language"],
                target_language=data["target_language"],
                level=selected,
            )
        )
        await state.clear()
        await message.answer("Profile saved. Use /lesson to generate a lesson.")

    @router.message(Command("lesson"))
    async def lesson(message: Message) -> None:
        try:
            _, generated = await service.create_lesson(message.from_user.id)
        except LookupError:
            await message.answer("Configure your profile first with /profile.")
            return
        words = "\n".join(
            f"• <b>{html.escape(item.term)}</b> — {html.escape(item.translation)}"
            for item in generated.vocabulary
        )
        await message.answer(
            f"<b>{html.escape(generated.title)}</b>\n\n"
            f"{html.escape(generated.explanation)}\n\n{words}",
            parse_mode=ParseMode.HTML,
        )

    @router.message(Command("review"))
    async def review(message: Message) -> None:
        due = repository.due_vocabulary(message.from_user.id, 5)
        if not due:
            await message.answer("Nothing is due for review yet.")
            return
        item = due[0]
        await message.answer(f"Translate: {item['term']}\nAnswer: ||{item['translation']}||")

    @router.message(Command("progress"))
    async def progress(message: Message) -> None:
        stats = repository.progress(message.from_user.id)
        await message.answer(f"Lessons: {stats['lessons']}\nVocabulary: {stats['vocabulary']}")

    return router


async def main() -> None:
    settings = Settings()
    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    repository = SQLiteRepository(settings.database)
    provider = (
        MockProvider()
        if settings.provider == "mock"
        else OpenAICompatibleProvider(settings.api_base_url, settings.api_key, settings.model)
    )
    service = LearningService(repository, provider)
    dispatcher = Dispatcher()
    dispatcher.include_router(create_router(service, repository))
    await dispatcher.start_polling(Bot(settings.telegram_token))


if __name__ == "__main__":
    asyncio.run(main())

