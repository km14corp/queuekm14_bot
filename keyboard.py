from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Data_base.db_help_class import db_help

button1 = InlineKeyboardButton('Да', callback_data='yes')
button2 = InlineKeyboardButton('Нет', callback_data='no')
keyboard_bool = InlineKeyboardMarkup().add(button1, button2)

button1 = InlineKeyboardButton('Записаться в очередь', callback_data='enroll')
button2 = InlineKeyboardButton('Просмотреть очередь', callback_data='view')
button3 = InlineKeyboardButton('Выписаться из очереди', callback_data='delete')
keyboard_start = InlineKeyboardMarkup(row_width=2).add(button2, button3, button1)


def make_markup(list_of_items):
    data_base = db_help('Data_base/queue.db')
    keyboard = InlineKeyboardMarkup()
    for index, item in enumerate(list_of_items):
        button = InlineKeyboardButton(item, callback_data=data_base.get_event_id(item))
        keyboard.add(button)
    return keyboard
