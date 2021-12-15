import os

from aiogram.types import ContentType
import string
import config
import logging
from Data_base.db_help_class import db_help
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

# initialise bot
data_base = db_help('Data_base/queue.db')
bot = Bot(token=config.TOKEN)
db = Dispatcher(bot)

make_pdf = False
photo_for_file = []



@db.message_handler(commands=["start"])
async def start(message: types.message):
    """The start method"""
    me = await bot.get_me()
    print(me)
    print(message)
    await bot.send_message(message.chat.id, message.chat.last_name+' '+message.chat.first_name)
    await message.answer('Я {} бот созданый с прихоти создателя для облегчения посылки дз\n Введите /help для '
                         'получениия большей информации'.format(me.first_name))

@db.message_handler(commands=['add'])
async def add(message: types.message):
    """The add method"""
    message.text = message.text.replace("/add ", "")
    message.text = message.text.strip()
    data_base.add_info('queue', ['name'], [str(message.text)])
@db.message_handler(commands=['delete'])
async def delete(message: types.message):
    """The delete method"""
    message.text = message.text.replace("/delete ", "")
    message.text = message.text.strip()
    data_base.delete_info('queue', ['name'], [str(message.text)])
@db.message_handler(commands=["queue"])
async def help(message: types.message):
    await message.answer('Привет {}, небольшая инструкция для получения тебе нужного pdf файла с картинок:\n1) Введи '
                         'команду /home_task\n2) Отправь поочередно нужные фото\n3) Введи /end и подожди создания '
                         'файла и его отправки тебе.'.format(message.chat.first_name))
    # data_base.add_info('queue', 'name', message.)
    print(message)

#tr
if __name__ == '__main__':
    executor.start_polling(db, skip_updates=True)

