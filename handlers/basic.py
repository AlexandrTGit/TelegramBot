from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from keyboards.keyboard import get_random_keyboard
from services.chat_gpt import ChatGptService

router = Router()

@router.message(Command('start'))
async def command_start(message: types.Message):
    await message.answer(f'Привет, {message.chat.first_name}!\n\n'
        'Доступные команды:\n'
        '/random - Случайный факт\n'
        '/gpt - Задать вопрос\n'
        '/talk - Поговорить со сказочным персонажем\n'
        '/quiz - Викторина'
    )

@router.message(Command('random'))

async def command_random(message: types.Message, gpt: ChatGptService):
    photo = FSInputFile("resources/images/random.jpg")
    msg = await message.answer_photo(
        photo=photo,
        caption="Идет генерация...",
    )

    with open("resources/prompts/random.txt", "r", encoding="utf-8") as file:
        prompt = file.read()

    answer = await gpt.send_question(prompt, "Дай случайный факт")

    await msg.edit_caption(
        caption=answer,
        reply_markup=get_random_keyboard()
    )

@router.callback_query(F.data == "random_more")
async def callback_random_more(callback: types.CallbackQuery, gpt: ChatGptService):
    await callback.answer()
    await command_random(callback.message, gpt)

@router.callback_query(F.data == "random_stop")
async def callback_random_stop(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Выход из режима фактов. Выбери новую команду меню")
