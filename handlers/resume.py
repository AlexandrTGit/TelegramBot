from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from keyboards.keyboard import build_dynamic_keyboard
from services.chat_gpt import ChatGptService
from utils.states import BotStates

router = Router()

@router.message(Command('resume'))
async def command_resume_start(message: types.Message, state: FSMContext):
    kb = build_dynamic_keyboard({
        "res_ca": "Канадский формат",
        "res_us": "Американский формат",
        "res_eu": "Европейский формат (CV)",
        "res_stop": "Отмена"
    })
    await message.answer("Выбери формат резюме:", reply_markup=kb)
    await state.set_state(BotStates.waiting_for_resume_format)

@router.callback_query(BotStates.waiting_for_resume_format, F.data.startswith("res_"))
async def process_resume_format(callback: types.CallbackQuery, state: FSMContext, gpt: ChatGptService):
    await callback.answer()

    if callback.data == "res_stop":
        await state.clear()
        await callback.message.answer("Отмена. Возврат в меню")
        return

    if callback.data == "res_ca":
        with open("resources/prompts/resume_ca.txt", "r", encoding="utf-8") as file:
            prompt = file.read()
    elif callback.data == "res_us":
        with open("resources/prompts/resume_us.txt", "r", encoding="utf-8") as file:
            prompt = file.read()
    elif callback.data == "res_eu":
        with open("resources/prompts/resume_eu.txt", "r", encoding="utf-8") as file:
            prompt = file.read()

    gpt.set_prompt(prompt)

    await callback.message.answer(
        "Соберем данные пошагово.\n\n<b>Шаг 1:</b> Напиши свое образование (ВУЗы, курсы, сертификаты).",
        parse_mode="HTML")
    await state.set_state(BotStates.waiting_for_education)

@router.message(BotStates.waiting_for_education)
async def process_education(message: types.Message, state: FSMContext):
    if message.text.startswith('/'):
        await state.clear()
        return

    await state.update_data(education=message.text)

    await message.answer("<b>Шаг 2:</b> Опиши свой опыт работы (где работал, что делал, какие достижения).",
                         parse_mode="HTML")
    await state.set_state(BotStates.waiting_for_experience)


@router.message(BotStates.waiting_for_experience)
async def process_experience(message: types.Message, state: FSMContext):
    if message.text.startswith('/'):
        await state.clear()
        return

    await state.update_data(experience=message.text)

    await message.answer("<b>Шаг 3:</b> Перечисли свои навыки.", parse_mode="HTML")
    await state.set_state(BotStates.waiting_for_skills)


@router.message(BotStates.waiting_for_skills)
async def process_skills(message: types.Message, state: FSMContext, gpt: ChatGptService):
    if message.text.startswith('/'):
        await state.clear()
        return

    msg = await message.answer("Идет обработка данных...")

    user_data = await state.get_data()
    education = user_data.get("education")
    experience = user_data.get("experience")
    skills = message.text

    final_text_for_gpt = (
        f"ОБРАЗОВАНИЕ:\n{education}\n\n"
        f"ОПЫТ РАБОТЫ:\n{experience}\n\n"
        f"НАВЫКИ:\n{skills}"
    )

    result = await gpt.add_message(final_text_for_gpt)

    kb = build_dynamic_keyboard({"search_jobs": "🔍 Найти вакансии под это резюме"})
    await msg.edit_text(result, reply_markup=kb)

    await state.clear()

@router.callback_query(F.data == "search_jobs")
async def process_job_search(callback: types.CallbackQuery, state: FSMContext, gpt: ChatGptService):
    await callback.answer()

    msg = await callback.message.answer("Анализирую рынок труда для тебя...")

    search_prompt = (
        "Ты — карьерный консультант. Проанализируй присланное ранее резюме и сделай следующее:\n"
        "1. Определи 3 наиболее подходящих названия должностей.\n"
        "2. Для каждой должности сформируй прямую ссылку на поиск вакансий в LinkedIn и Indeed.\n"
        "3. Ссылки должны выглядеть так: https://www.linkedin.com/jobs/search/?keywords=НАЗВАНИЕ_ДОЛЖНОСТИ\n"
        "4. Выдай ответ в виде списка: Название должности — Ссылка на LinkedIn — Ссылка на Indeed.\n"
        "Пиши кратко и только по делу."
    )

    result = await gpt.add_message(search_prompt)

    await msg.edit_text(f"Вот что мне удалось найти под твой профиль:\n\n{result}", disable_web_page_preview=True)