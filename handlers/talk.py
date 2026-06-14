from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.keyboard import get_talk_keyboard
from services.chat_gpt import ChatGptService
from utils.states import BotStates

router = Router()

@router.message(Command('talk'))
async def command_talk_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Выбери, с кем из героев сказок ты хочешь поговорить:",
        reply_markup=get_talk_keyboard()
    )
    await state.set_state(BotStates.waiting_for_hero_choice)


@router.callback_query(BotStates.waiting_for_hero_choice, F.data.startswith("talk_"))
async def process_hero_choice(callback: types.CallbackQuery, state: FSMContext, gpt: ChatGptService):
    await callback.answer()

    if callback.data == "talk_stop":
        await state.clear()
        await callback.message.answer("Диалог завершен.")
        return

    if callback.data == "talk_yaga":
        hero_name = "Бабой-Ягой"
        with open("resources/prompts/talk_yaga.txt", "r", encoding="utf-8") as file:
            prompt = file.read()
    elif callback.data == "talk_koschei":
        hero_name = "Кощеем Бессмертным"
        with open("resources/prompts/talk_koschei.txt", "r", encoding="utf-8") as file:
            prompt = file.read()
    elif callback.data == "talk_leshy":
        hero_name = "Лешим"
        with open("resources/prompts/talk_leshy.txt", "r", encoding="utf-8") as file:
            prompt = file.read()

    gpt.set_prompt(prompt)

    await callback.message.answer(f"Ты начал диалог с {hero_name}:")

    await state.set_state(BotStates.talking_with_hero)

@router.message(BotStates.talking_with_hero)
async def process_hero_dialog(message: types.Message, state: FSMContext, gpt: ChatGptService):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Диалог прерван другой командой.")
        return

    msg = await message.answer("Собеседник печатает...")
    answer = await gpt.add_message(message.text)

    stop_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Закончить диалог", callback_data="talk_stop")]
    ])

    await msg.edit_text(answer, reply_markup=stop_kb)

@router.callback_query(BotStates.talking_with_hero, F.data == "talk_stop")
async def stop_dialog_in_process(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer("Диалог завершен. Выбери новую команду из меню")