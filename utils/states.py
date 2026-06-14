from aiogram.fsm.state import StatesGroup, State

class BotStates(StatesGroup):
    waiting_for_gpt_question = State()
    waiting_for_hero_choice = State()
    talking_with_hero = State()
    waiting_for_quiz_theme = State()
    waiting_for_quiz_answer = State()
    waiting_for_resume_format = State()
    waiting_for_education = State()
    waiting_for_experience = State()
    waiting_for_skills = State()
    waiting_for_job_search = State()