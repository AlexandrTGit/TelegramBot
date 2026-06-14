from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from keyboards.keyboard import build_dynamic_keyboard
from services.chat_gpt import ChatGptService
from utils.states import BotStates

router = Router()

@router.message(Command('quiz'))
async def command_quiz_start(message: types.Message, state: FSMContext):
    kb = build_dynamic_keyboard({
        "quiz_python": "Python и алгоритмы",
        "quiz_myth": "Славянская мифология",
        "quiz_games": "Видеоигры",
        "quiz_stop": "Отмена"
    })

    await message.answer("Выбери тему для викторины:", reply_markup=kb)
    await state.set_state(BotStates.waiting_for_quiz_theme)

@router.callback_query(BotStates.waiting_for_quiz_theme, F.data.startswith("quiz_"))
async def process_quiz_theme(callback: types.CallbackQuery, state: FSMContext, gpt: ChatGptService):
    await callback.answer()

    if callback.data == "quiz_stop":
        await state.clear()
        await callback.message.answer("Викторина отменена. Возвращайся в меню")
        return

    theme_key = callback.data.replace("quiz_", "")

    themes_dict = {
        "python": "основам программирования на Python",
        "myth": "славянским мифам, сказкам и фольклору",
        "games": "индустрии видеоигр и геймдеву"
    }

    selected_theme = themes_dict.get(theme_key)

    gpt.set_prompt(
        f"Ты строгий, но справедливый ведущий викторины. Задай мне один интересный вопрос по теме: {selected_theme}. Не пиши ответ, не давай варианты (А, Б, В), просто задай вопрос, чтобы я мог напечатать ответ словами.")

    msg = await callback.message.answer("Придумываю каверзный вопрос... ")

    # Нейросеть генерирует вопрос
    question = await gpt.add_message("Задай свой вопрос.")

    # Выдаем вопрос и переключаем режим
    await msg.edit_text(f"Вопрос:\n\n{question}")
    await state.set_state(BotStates.waiting_for_quiz_answer)


@router.message(BotStates.waiting_for_quiz_answer)
async def process_quiz_answer(message: types.Message, state: FSMContext, gpt: ChatGptService):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Викторина прервана.")
        return

    msg = await message.answer("Проверяю ответ...")

    evaluation = await gpt.add_message(
        f"Мой ответ: {message.text}. Оцени, правильно ли это? Если не угадал — назови правильный ответ и объясни почему.")

    kb = build_dynamic_keyboard({"quiz_restart": "Сыграть еще раз"})

    await msg.edit_text(evaluation, reply_markup=kb)

    await state.clear()

@router.callback_query(F.data == "quiz_restart")
async def restart_quiz(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await command_quiz_start(callback.message, state)