import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

import asyncio
import logging
from aiogram import F, Bot, Dispatcher, types
from aiogram.filters.command import Command

import api
import config
import qr
import sqlite3

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
router = Router()
dp = Dispatcher(bot=bot, storage=storage)
dp.include_router(router)
conn = sqlite3.connect('tokens.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS user_tokens (user_id INTEGER PRIMARY KEY, token TEXT)''')


async def save_token(user_id, token):
    c.execute('REPLACE INTO user_tokens (user_id, token) VALUES (?, ?)', (user_id, token))
    conn.commit()


async def get_token(user_id):
    c.execute('SELECT token FROM user_tokens WHERE user_id = ?', (user_id,))
    return c.fetchone()


@dp.message(F.text.lower() == "/start")
async def with_puree(message: types.Message):
    await message.reply("регистрация /register \nзагрузить продукты в холодильник /myholands")


data = {}


class AwaitMessages(StatesGroup):
    fio_add = State()
    phone_add = State()


class ChosenFridge(StatesGroup):
    fridge = State()


@router.message(Command('register'))
async def command_start(message: types.Message, state: FSMContext):
    await message.answer(
        text="Напишите ваше имя пользователя:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AwaitMessages.fio_add)


@router.message(AwaitMessages.fio_add)
async def process_fio_add(message: types.Message, state: FSMContext):
    data['name'] = message.text
    await message.answer(
        text='Введите пароль:',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AwaitMessages.phone_add)


@router.message(AwaitMessages.phone_add)
async def process_fio_add(message: types.Message, state: FSMContext):
    data['phone'] = message.text

    try:
        user_id = message.from_user.id
        token = api.login(data['name'], data['phone'])['auth_token']
        await save_token(user_id, token)
        await message.answer(f'имя пользователя - {data["name"]}\nпароль - {data["phone"]}')
    except:
        await message.answer('неправильные логин или паролью. попробуйте ещё раз')

    await state.clear()


@dp.message(Command("myholands"))
async def cmd_start(message: types.Message, state: FSMContext):
    token = await get_token(message.from_user.id)
    token = token[0]
    fridges = api.get_all_fridges(token)
    print(fridges)
    kb = []
    for i in fridges:
        kb.append([types.KeyboardButton(text=i['name'])])
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите холодильник"
    )
    await message.answer("Выберите холодильник", reply_markup=keyboard)
    await state.set_state(ChosenFridge.fridge)



@router.message(ChosenFridge.fridge)
async def process_fio_add(message: types.Message, state: FSMContext):
    fridge = message.text
    token = await get_token(message.from_user.id)
    token = token[0]
    fridges = api.get_all_fridges(token)
    fridge_id = 0
    for f in fridges:
        if fridge == f['name']:
            fridge_id = f['id']

    await message.reply("отправьте QR-код")

    @dp.message(F.photo)
    async def photo_handler(message: types.Message):
        photo_data = message.photo[-1]
        file_name = f"photos/{photo_data.file_id}.jpg"
        await bot.download(photo_data, destination=file_name)
        link = qr.read_qr(file_name)
        api.send_qr(link, fridge_id, token)
        await message.answer(f'продукты были добавлены в холодильник {fridge}')


from aiogram import F


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
