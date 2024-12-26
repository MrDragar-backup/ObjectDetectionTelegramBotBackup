import asyncio
import logging
import tempfile
from collections import Counter

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from src.services import recognize_objects, process_plate

router = Router()
file_id_storage: dict[str, str] = {}


@router.message(Command("help"))
@router.message(CommandStart())
async def start(message: Message):
    await message.reply(
        text="Привет. Я помогу тебе определить объекты из твоей фотографии.\n"
             f"Просто отправь мне картинку, и я пришлю тебе ответ."
    )


@router.message(F.photo)
async def handle_photo(message: Message):
    file_id = message.photo[-1].file_id

    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    downloaded_file = await message.bot.download_file(file_path)
    with tempfile.NamedTemporaryFile(
            delete=True, suffix=".jpg",
            dir=tempfile.gettempdir()) as temp_file:
        temp_file_path = temp_file.name

        with open(temp_file_path, "wb") as f:
            read_file = await asyncio.to_thread(downloaded_file.read)
            await asyncio.to_thread(f.write, read_file)
        try:
            objects = recognize_objects(temp_file_path)
        except Exception as ex:
            logging.info(ex)
            return await message.reply(f"Объекты не найдены")
        if "plate_of_groceries" not in objects:
            result = [
                f"{label} - {count}"
                for label, count in objects.items()
            ]
            text = f"Распознанные объекты: \n\n{"\n".join(result)}"
            return await message.reply(text)

        try:
            groceries = process_plate(temp_file_path)
            result = [
                f"{label} - {count}%"
                for label, count in groceries.items()
            ]
            text = f"Содержимое тарелки с продуктами: \n\n{"\n".join(result)}"
            await message.reply(text)
        except Exception as ex:
            logging.debug(ex)
            return await message.reply(f"Произошла ошибка при обработке тарелки")
