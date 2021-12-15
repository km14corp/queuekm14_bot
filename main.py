import logging

from aiogram import Bot, Dispatcher, executor, types

import config
from Data_base.db_help_class import db_help

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
    await bot.send_message(message.chat.id, message.chat.last_name + ' ' + message.chat.first_name)
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


@db.message_handler(commands=['show_var'])
async def show_variants(message: types.message):
    """The show variants method"""
    for i, j in enumerate(data_base.have_db()):
        await message.answer(str(i+1) + ') ' + j)


@db.message_handler(commands=['show_table'])
async def show_table(message: types.message):
    """The show table method"""
    message.text = message.text.replace("/show_table ", "")
    message.text = message.text.strip()
    print(message.text)
    data = data_base.return_info(message.text, 'name')  # not sure about arguments
    for i,j in enumerate(data):
        await message.answer(str(i+1)+') '+j[0])


# tr
if __name__ == '__main__':
    executor.start_polling(db, skip_updates=True)
