import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton

from Data_base.db_help_class import db_help
from keybord import keyboard_bool, make_markup, keyboard_start
import config
import schedule_parser as sc

url = "http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?g=8bb9bcf6-5db2-4124-8c1a-d0debc152bc9"

logging.basicConfig(level=logging.INFO)

# initialise bot
data_base = db_help('Data_base/queue.db')
bot = Bot(token=config.TOKEN)
dispatcher = Dispatcher(bot, storage=MemoryStorage())


class State_machine(StatesGroup):
    VIEW_STATE = State()
    START_STATE = State()
    DELETE_STATE = State()
    ENROLL_STATE = State()
    NAME_STATE = State()
    NAME_FLAG_STATE = State()
    QUEUE_STATE = State()
    YES_STATE = State()
    NO_STATE = State()


@dispatcher.message_handler(commands=["start"], state='*')
async def start(message: types.message):
    """The start method"""
    await bot.send_message(message.from_user.id,
                           "Привет, я бот для того чтобы записываться в очередь, только для КМ-14😜",
                           reply_markup=keyboard_start)

    await State_machine.START_STATE.set()


@dispatcher.callback_query_handler(lambda c: c.data == 'enroll', state=State_machine.START_STATE)
async def enroll(callback_query: types.CallbackQuery):
    subs = data_base.get_info('courses')
    for sub in subs:
        print(sub)
        sc.queue_manager(sub[1], url)
    await State_machine.ENROLL_STATE.set()
    await get_name(callback_query)


@dispatcher.callback_query_handler(lambda c: c.data == 'view', state=State_machine.START_STATE)
async def view(callback_query: types.CallbackQuery):
    queues = list(data_base.get_all_tables())
    queues.remove('users')
    queues.remove('courses')
    if len(queues) != 0:
        await bot.send_message(callback_query.from_user.id, "Выбери очередь, которую хочешь просмотреть",
                               reply_markup=make_markup(queues))
        await State_machine.VIEW_STATE.set()
    else:
        await bot.send_message(callback_query.from_user.id, "В данный момент нет никаких очередей")
        await State_machine.START_STATE.set()
        await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                               reply_markup=keyboard_start)



@dispatcher.callback_query_handler(lambda c: c.data == 'delete', state=State_machine.START_STATE)
async def get_queue_to_delete(callback_query: types.CallbackQuery):
    queues = list(data_base.get_all_tables())
    queues.remove('users')
    queues.remove('courses')
    if len(queues) != 0:
        await bot.send_message(callback_query.from_user.id, "Выбери очередь, из которой хочешь выписаться",
                               reply_markup=make_markup(queues).add(InlineKeyboardButton('Назад⬅', callback_data='back')))
        await State_machine.DELETE_STATE.set()
    else:
        await bot.send_message(callback_query.from_user.id, "В данный момент нет никаких очередей")
        await State_machine.START_STATE.set()
        await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                               reply_markup=keyboard_start)


@dispatcher.callback_query_handler(lambda c: c.data == 'back', state=State_machine.DELETE_STATE)
async def get_back(callback_query: types.CallbackQuery):
    await State_machine.START_STATE.set()
    await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                           reply_markup=keyboard_start)


@dispatcher.callback_query_handler(state=State_machine.DELETE_STATE)
async def delete(callback_query: types.CallbackQuery):
    if not data_base.check_id_in_queue(callback_query.from_user.id, callback_query.data):
        await bot.send_message(callback_query.from_user.id, "Вы не записывались в эту очередь")
    else:
        data_base.delete_info(callback_query.data, 'id', str(callback_query.from_user.id))
        await bot.send_message(callback_query.from_user.id, "Вы были успешно удалены из этой очереди")
    await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                           reply_markup=keyboard_start)
    await State_machine.START_STATE.set()


@dispatcher.callback_query_handler(state=State_machine.VIEW_STATE)
async def get_queue(callback_query: types.CallbackQuery):
    message = ""
    for x in data_base.return_info(callback_query.data):
        message += (str(x[0]) + ") " + str(data_base.return_name(x[1])) + "\n")
    if len(message) == 0:
        await bot.send_message(callback_query.from_user.id, "Эта очередь пустая")
    else:
        await bot.send_message(callback_query.from_user.id, message)
    await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                           reply_markup=keyboard_start)
    await State_machine.START_STATE.set()


@dispatcher.callback_query_handler(lambda c: c.data == 'enroll', state=State_machine.ENROLL_STATE)
async def get_name(callback_query: types.CallbackQuery):
    if not data_base.return_name(callback_query.from_user.id):
        name = ""
        if callback_query.from_user.first_name is not None:
            name += callback_query.from_user.first_name
        name += " "
        if callback_query.from_user.last_name is not None:
            name += callback_query.from_user.last_name
    else:
        name = data_base.return_name(callback_query.from_user.id)

    await bot.send_message(callback_query.from_user.id, "Хочешь ли записаться под именем\n" + name + "?",
                           reply_markup=keyboard_bool)

    await State_machine.NAME_FLAG_STATE.set()


@dispatcher.callback_query_handler(lambda c: c.data == 'yes', state=State_machine.NAME_FLAG_STATE)
async def press_yes(callback_query: types.CallbackQuery):
    if not data_base.return_name(callback_query.from_user.id):
        name = ""
        if callback_query.from_user.first_name is not None:
            name += callback_query.from_user.first_name
        name += " "
        if callback_query.from_user.last_name is not None:
            name += callback_query.from_user.last_name
        data_base.add_name_id(str(callback_query.from_user.id),
                              name)
    queues = list(data_base.get_all_tables())
    queues.remove('users')
    queues.remove('courses')
    if len(queues) != 0:
        await bot.send_message(callback_query.from_user.id, "Выбери очередь, в которую хочешь записаться",
                               reply_markup=make_markup(queues))
        await State_machine.YES_STATE.set()
    else:
        await bot.send_message(callback_query.from_user.id, "В данный момент нет никаких очередей")
        await State_machine.START_STATE.set()
        await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                               reply_markup=keyboard_start)


@dispatcher.callback_query_handler(lambda c: c.data == 'no', state=State_machine.NAME_FLAG_STATE)
async def press_no(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите имя\n")
    await State_machine.NO_STATE.set()


@dispatcher.message_handler(state=State_machine.NO_STATE)
async def set_name(message: types.Message):
    if not data_base.return_name(message.from_user.id):
        data_base.add_name_id(str(message.from_user.id), message.text)
    else:
        data_base.update_name(message.from_user.id, message.text)
    name = data_base.return_name(message.from_user.id)

    await bot.send_message(message.from_user.id, "Хочешь ли записаться под именем\n" + name + "?",
                           reply_markup=keyboard_bool)

    await State_machine.NAME_FLAG_STATE.set()


@dispatcher.callback_query_handler(state=State_machine.YES_STATE)
async def join_queue(callback_query: types.CallbackQuery):
    message = ""

    if not data_base.check_id_in_queue(callback_query.from_user.id, callback_query.data):
        data_base.add_info(callback_query.data, ['number', 'id'],
                           [str(len(data_base.return_info(callback_query.data)) + 1),
                            str(callback_query.from_user.id)])
        await bot.send_message(callback_query.from_user.id, "Ты успешно записался в очередь " + callback_query.data)
    else:
        await bot.send_message(callback_query.from_user.id, "Вы уже записаны в эту очередь")
    print(data_base.return_info(callback_query.data))
    for x in data_base.return_info(callback_query.data):
        message += (str(x[0]) + ") " + str(data_base.return_name(x[1])) + "\n")
    await bot.send_message(callback_query.from_user.id, message)
    await State_machine.START_STATE.set()
    await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                           reply_markup=keyboard_start)


@dispatcher.message_handler(state='*', commands=['add_course'])
async def admin_course_add(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766]:
        data_base.add_info('courses', 'name', message.get_args())


@dispatcher.message_handler(state='*', commands=['delete_course'])
async def admin_course_delete(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766]:
        data_base.delete_info('courses', 'name', message.get_args())


@dispatcher.message_handler(state='*', commands=['add_queue'])
async def admin_queue_add(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766]:
        data_base.make_db(message.get_args())


@dispatcher.message_handler(state='*', commands=['delete_queue'])
async def admin_queue_delete(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766]:
        data_base.delete_db(message.get_args())


@dispatcher.message_handler(state='*', commands=['show_table'])
async def admin_course_add(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766]:
        table = [str(i) for i in data_base.get_info(message.get_args())]

        await bot.send_message(message.from_user.id, '\n'.join(table))


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)