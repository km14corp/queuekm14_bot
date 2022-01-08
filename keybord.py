from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Data_base.db_help_class import db_help

button1 = InlineKeyboardButton('Да', callback_data='yes')
button2 = InlineKeyboardButton('Нет', callback_data='no')
keyboard_bool = InlineKeyboardMarkup().add(button1, button2)

button1 = InlineKeyboardButton('Записаться в очередь', callback_data='enroll')
button2 = InlineKeyboardButton('Просмотреть очередь', callback_data='view')
keyboard_start = InlineKeyboardMarkup().add(button1, button2)

def make_markup(list_of_items):
    keyboard = InlineKeyboardMarkup()
    for item in list_of_items:
        button = InlineKeyboardButton(item, callback_data=item)
        keyboard.add(button)
    return keyboard
