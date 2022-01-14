import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton

from Data_base.db_help_class import db_help
from keybord import keyboard_bool, make_markup, keyboard_start
import config
from schedule_parse import Parser
import asyncio
import aioschedule

schedule_url = "http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?g=8bb9bcf6-5db2-4124-8c1a-d0debc152bc9"

logging.basicConfig(level=logging.INFO)

# initialise bot
data_base = db_help('Data_base/queue.db')
parser = Parser(schedule_url, data_base)
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



@dispatcher.message_handler(commands=["help"], state='*')
async def help(message: types.message):
    """The start method"""
    await bot.send_message(message.from_user.id, "Админские команды: \n"
                                                 "/add_course - Добавить курс\n"
                                                 "/delete_course - Удалить курс\n"
                                                 "/show_users - Вывести таблицу users\n"
                                                 "/show_courses - Вывести таблицу courses\n"
                                                 "/show_events - Вывести таблицу events")

    await State_machine.START_STATE.set()


@dispatcher.message_handler(commands=["start"], state='*')
async def start(message: types.message):
    """The start method"""
    await bot.send_message(message.from_user.id,
                           "Привет, я бот для того чтобы записываться в очередь, только для КМ-14😜",
                           reply_markup=keyboard_start)

    await State_machine.START_STATE.set()


@dispatcher.callback_query_handler(lambda c: c.data == 'enroll', state=State_machine.START_STATE)
async def enroll(callback_query: types.CallbackQuery):
    # subs = data_base.get_info('courses')
    await State_machine.ENROLL_STATE.set()
    await get_name(callback_query)


@dispatcher.callback_query_handler(lambda c: c.data == 'view', state=State_machine.START_STATE)
async def view(callback_query: types.CallbackQuery):
    events = data_base.get_events()
    if len(events) != 0:
        await bot.send_message(callback_query.from_user.id, "Выбери очередь, которую хочешь просмотреть",
                               reply_markup=make_markup(events))
        await State_machine.VIEW_STATE.set()
    else:
        await bot.send_message(callback_query.from_user.id, "В данный момент нет никаких очередей")
        await State_machine.START_STATE.set()
        await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                               reply_markup=keyboard_start)


@dispatcher.callback_query_handler(lambda c: c.data == 'delete', state=State_machine.START_STATE)
async def get_queue_to_delete(callback_query: types.CallbackQuery):
    events = data_base.get_events()
    if len(events) != 0:
        await bot.send_message(callback_query.from_user.id, "Выбери очередь, из которой хочешь выписаться",
                               reply_markup=make_markup(events).add(
                                   InlineKeyboardButton('Назад⬅', callback_data='back')))
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
    if not data_base.is_booked(callback_query.from_user.id, callback_query.data):
        await bot.send_message(callback_query.from_user.id, "Вы не записывались в эту очередь")
    else:
        data_base.unbook_user(callback_query.from_user.id, callback_query.data)
        await bot.send_message(callback_query.from_user.id, "Вы были успешно удалены из очереди " + data_base.get_event_name(callback_query.data))
    await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                           reply_markup=keyboard_start)
    await State_machine.START_STATE.set()


@dispatcher.callback_query_handler(state=State_machine.VIEW_STATE)
async def get_queue(callback_query: types.CallbackQuery):
    message = ""
    for index, user_name in data_base.get_event_queue(callback_query.data):
        message += (str(index) + ") " + user_name + "\n")
    if len(message) == 0:
        await bot.send_message(callback_query.from_user.id, "Эта очередь пустая")
    else:
        await bot.send_message(callback_query.from_user.id, message)
    await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                           reply_markup=keyboard_start)
    await State_machine.START_STATE.set()


@dispatcher.callback_query_handler(lambda c: c.data == 'enroll', state=State_machine.ENROLL_STATE)
async def get_name(callback_query: types.CallbackQuery):
    if not data_base.is_user_present(callback_query.from_user.id):
        name = ""
        if callback_query.from_user.first_name is not None:
            name += callback_query.from_user.first_name
        name += " "
        if callback_query.from_user.last_name is not None:
            name += callback_query.from_user.last_name
    else:
        name = data_base.get_user_name(callback_query.from_user.id)

    await bot.send_message(callback_query.from_user.id, "Хочешь ли записаться под именем\n" + name + "?",
                           reply_markup=keyboard_bool)

    await State_machine.NAME_FLAG_STATE.set()


@dispatcher.callback_query_handler(lambda c: c.data == 'yes', state=State_machine.NAME_FLAG_STATE)
async def press_yes(callback_query: types.CallbackQuery):
    if not data_base.is_user_present(callback_query.from_user.id):
        name = ""
        if callback_query.from_user.first_name is not None:
            name += callback_query.from_user.first_name
        name += " "
        if callback_query.from_user.last_name is not None:
            name += callback_query.from_user.last_name
        data_base.add_user(callback_query.from_user.id, name)
    events = data_base.get_events()
    if len(events) != 0:
        await bot.send_message(callback_query.from_user.id, "Выбери очередь, в которую хочешь записаться",
                               reply_markup=make_markup(events))
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
    if not data_base.get_user_name(str(message.from_user.id)):
        data_base.add_user(message.from_user.id, message.text)
    else:
        data_base.update_user_name(message.from_user.id, message.text)
    name = data_base.get_user_name(str(message.from_user.id))

    await bot.send_message(message.from_user.id, "Хочешь ли записаться под именем\n" + name + "?",
                           reply_markup=keyboard_bool)

    await State_machine.NAME_FLAG_STATE.set()


@dispatcher.callback_query_handler(state=State_machine.YES_STATE)
async def join_queue(callback_query: types.CallbackQuery):
    message = ""

    if not data_base.is_booked(callback_query.from_user.id, callback_query.data):
        data_base.book_user(callback_query.from_user.id, callback_query.data)
        await bot.send_message(callback_query.from_user.id, "Ты успешно записался в очередь " + data_base.
                               get_event_name(callback_query.data))
    else:
        await bot.send_message(callback_query.from_user.id, "Вы уже записаны в эту очередь")
    for index, user_name in data_base.get_event_queue(callback_query.data):
        message += (str(index) + ") " + user_name + "\n")
    await bot.send_message(callback_query.from_user.id, message)
    await State_machine.START_STATE.set()
    await bot.send_message(callback_query.from_user.id, "Что дальше?)",
                           reply_markup=keyboard_start)


@dispatcher.message_handler(state='*', commands=['add_course'])
async def admin_course_add(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766, 418206061] and len(message.get_args()) != 0:
        data_base.add_info('courses', 'name', message.get_args())


@dispatcher.message_handler(state='*', commands=['delete_course'])
async def admin_course_delete(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766, 418206061] and len(message.get_args()) != 0:
        data_base.delete_course(message.get_args())


@dispatcher.message_handler(state='*', commands=['show_users'])
async def admin_course_delete(message: types.Message):
    temp_message = ""
    users = data_base.get_users()
    for index, user in enumerate(users):
        temp_message += str(int(index) + 1) + ') ' + str(user[0]) + ' ' + str(user[1]) + '\n'
    temp_message += f'\n There are {len(users)} users'
    if message.from_user.id in [327601961, 405856902, 558259766, 418206061]:
        await bot.send_message(message.from_user.id, temp_message)


@dispatcher.message_handler(state='*', commands=['show_courses'])
async def admin_course_delete(message: types.Message):
    temp_message = ""
    courses = data_base.get_courses()
    for index, course in enumerate(courses):
        temp_message += str(int(index) + 1) + ') ' + str(course[0]) + ' ' + str(course[1]) + '\n'
    temp_message += f'\n There are {len(courses)} courses'
    if message.from_user.id in [327601961, 405856902, 558259766, 418206061]:
        await bot.send_message(message.from_user.id, temp_message)


@dispatcher.message_handler(state='*', commands=['show_events'])
async def admin_course_delete(message: types.Message):
    temp_message = ""
    events = data_base.get_events()
    for index, event in enumerate(events):
        temp_message += str(int(index) + 1) + ') ' + str(event) + '\n'
    temp_message += f'\n There are {len(events)} events'
    if message.from_user.id in [327601961, 405856902, 558259766, 418206061]:
        await bot.send_message(message.from_user.id, temp_message)


@dispatcher.message_handler(state='*', commands=['add_event'])
async def admin_event_delete(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766, 418206061] and len(message.get_args()) != 0:
        data_base.add_event("something_else", message.get_args())


@dispatcher.message_handler(state='*', commands=['delete_event'])
async def admin_event_delete(message: types.Message):
    if message.from_user.id in [327601961, 405856902, 558259766, 418206061] and len(message.get_args()) != 0:
        data_base.delete_event("something_else", message.get_args())


async def queue_update():
    subs = data_base.get_courses('name')
    for sub in subs:
        parser.update_events(sub)

        # print(f"No queues update for {sub}")


async def scheduler():
    aioschedule.every().day.at("21:41").do(queue_update)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True, on_startup=on_startup)
