from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from services.chat_gpt import ChatGptService
from utils.states import BotStates

router = Router()

@router.message(Command('gpt'))
async def command_gpt_start(message: types.Message, state: FSMContext):

    await message.answer("Привет! Задай любой вопрос чату GPT:")

    await state.set_state(BotStates.waiting_for_gpt_question)

@router.message(BotStates.waiting_for_gpt_question)
async def process_gpt_question(message: types.Message, state: FSMContext, gpt: ChatGptService):

    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Режим диалога с GPT прерван.")
        return

    msg = await message.answer("Думаю...")

    prompt = "Ты полезный и краткий ассистент."
    answer = await gpt.send_question(prompt, message.text)

    await msg.edit_text(answer)

    await message.answer("Можешь задать еще один вопрос или выбери команду в меню.")
