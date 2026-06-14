import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from services.chat_gpt import ChatGptService
from handlers import basic
from handlers import gpt
from handlers import talk
from handlers import quiz
from handlers import resume_handler

async def main():

    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    TOKEN_TG = os.getenv("BOT_TOKEN")
    TOKEN_AI = os.getenv("AI_TOKEN")

    bot = Bot(token=TOKEN_TG)
    dp = Dispatcher()
    gpt_service = ChatGptService(TOKEN_AI)

    dp.include_router(basic.router)
    dp.include_router(gpt.router)
    dp.include_router(talk.router)
    dp.include_router(quiz.router)
    dp.include_router(resume_handler.router)

    print("Диспетчер запущен, бот готов к работе")
    await dp.start_polling(bot, gpt=gpt_service)

if __name__ == '__main__':
    asyncio.run(main())