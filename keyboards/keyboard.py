from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_random_keyboard() -> InlineKeyboardMarkup:
    more_btn = InlineKeyboardButton(text="Хочу еще факт", callback_data="random_more")
    stop_btn = InlineKeyboardButton(text="Закончить", callback_data="random_stop")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [more_btn],
        [stop_btn]
    ])

    return keyboard

def get_talk_keyboard() -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Баба-Яга", callback_data="talk_yaga")],
        [InlineKeyboardButton(text="Кощей Бессмертный", callback_data="talk_koschei")],
        [InlineKeyboardButton(text="Леший", callback_data="talk_leshy")],
        [InlineKeyboardButton(text="Закончить диалог", callback_data="talk_stop")]
    ])
    return keyboard


def build_dynamic_keyboard(buttons_data: dict) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    for callback, text in buttons_data.items():
        builder.button(text=text, callback_data=callback)

    builder.adjust(1)

    return builder.as_markup()