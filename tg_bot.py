from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
import os
import logging
from random import choice
from datetime import datetime

from owm_weather import get_weather_data as get_owm_weather
from gismeteo_weather import get_weather as get_gismeteo_weather
import utils
import bot_keyboard


logger = logging.getLogger(name='weather.tg_bot')
logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class BotStatesGroup(StatesGroup):
    owm_city = State()
    gismeteo_city = State()


async def on_startup(_):
    logger.info('Бот запущен.')

async def on_shutdown(_):
    logger.info('Бот завершил работу.')


def get_weather(site: str, city: str = '') -> str:
    now = datetime.now().strftime('%d.%m.%Y %H:%M')
    weather_data_str = f'<em>ℹ️ Данные на {now}</em>\n'

    if site == 'owm':
        weather_data = get_owm_weather(city=city)
        weather_data_str += utils.make_owm_weather_data_string(weather_data)
    elif site == 'gismeteo':
        weather_data = get_gismeteo_weather(city='')
        weather_data_str += utils.make_gismeteo_weather_data_string(weather_data)
    return weather_data_str


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message) -> None:
    kb = bot_keyboard.make_start_keyboard()
    await bot.send_message(
        chat_id=message.from_id, 
        text='Привет! Я <b>TenkiBot</b>, с моей помощью можно узнать погоду в твоем городе и не только.\nВыбери сайт, с которого будут взяты данные о погоде.',
        reply_markup=kb,
        parse_mode='HTML'
    )


@dp.message_handler(commands=['about'])
async def send_description(message: types.Message) -> None:
    description = '''
        <b><em>TenkiBot v1.0</em></b>
        Бот умеет собирать данные о погоде с сайтов <b>OpenWeatherMap</b> и <b>Gismeteо</b>.
        Перед началом поиска данных можно выбрать сайт, с которого будут взяты эти данные.
        <em>Данные о погоде от разных сайтов могут отличаться.</em>

        <em>С сайта OpenWeatherMap бот может получить погоду в разных городах по запросу.</em>
        <em>С сайта Gismeteo бот собирает данные о погоде из города по предполагаемому местоположению (его определяет сам сайт Gismeteo).</em>
    '''
    await message.answer(description, parse_mode='HTML')


@dp.message_handler()
async def heart_echo(message: types.Message) -> None:
    if message.text in '❤️💗💞💕💖🥰😘🧡💛💚💙💜🖤🤍🤎💝💓💟':
        heart = choice( ['❤️', '💛', '🧡', '💜'] )
        await message.answer(heart)


async def print_weather_data(site: str, message: types.Message, city:str|None=None) -> None:
    kb = bot_keyboard.make_back_button_keyboard()
    try:
        if city is not None:
            weather_info = get_weather(site=site, city=city)
        else:
            weather_info = get_weather(site)
        await message.answer(weather_info, parse_mode='HTML', reply_markup=kb)
    except KeyError:
        await message.answer('Такого города не существует либо название города введено неверно. Нажмите /start и попробуйте ввести город снова.', reply_markup=kb)
    except Exception as exc:
        logger.error(exc)
        await message.answer('Во время поиска информации о погоде возникла ошибка.', reply_markup=kb)


async def load_city(message: types.Message, state: FSMContext, site: str) -> None:
    async with state.proxy() as data:
        data['city'] = message.text
    await print_weather_data(site='owm', city=data['city'], message=message)
    await state.finish()


@dp.message_handler(state=BotStatesGroup.owm_city) 
async def load_owm_city(message: types.Message, state: FSMContext) -> None:
    await load_city(message, state, site='owm')


# @dp.message_handler(state=BotStatesGroup.gismeteo_city)
# async def load_gismeteo_city(message: types.Message, state: FSMContext) -> None:
#     await load_city(message, state, site='gismeteo')


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery) -> None:
    match callback.data:
        case 'owm':
            await callback.message.answer('Введите город, для которого хотите получить информацию о погоде.')
            await BotStatesGroup.owm_city.set()   
        case 'gismeteo':
            await print_weather_data(site='gismeteo', message=callback.message)
            # await callback.message.answer('Введите город, для которого хотите получить информацию о погоде.')
            # await BotStatesGroup.gismeteo_city.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
