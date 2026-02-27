import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ParseMode
import aiohttp

# ========== ТОКЕНЫ ПРЯМО В КОДЕ ==========
BOT_TOKEN = "8628470329:AAGNu__7pUBGbxo5UoRehztxrxHqsNrayFM"
WEATHER_API_KEY = "3a678ada131c76b2d68e764b1a4301c4"
# =========================================

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Клавиатура с одной кнопкой
def get_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🌤 Узнать погоду"))
    return keyboard

# Функция получения погоды
async def get_weather(city: str) -> dict:
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'success': True,
                        'city': data['name'],
                        'country': data['sys']['country'],
                        'temp': data['main']['temp'],
                        'feels_like': data['main']['feels_like'],
                        'humidity': data['main']['humidity'],
                        'description': data['weather'][0]['description']
                    }
                else:
                    return {'success': False, 'error': 'Город не найден'}
        except Exception as e:
            return {'success': False, 'error': 'Ошибка соединения'}

# Команда /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 <b>Привет! Я погодный бот.</b>\n\n"
        "Просто отправь мне название города, и я покажу погоду!\n"
        "Например: Москва, Лондон, Париж"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML, reply_markup=get_keyboard())

# Команда /help
@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    help_text = (
        "🔍 <b>Как пользоваться:</b>\n\n"
        "1. Отправь название города\n"
        "2. Нажми кнопку \"🌤 Узнать погоду\""
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)

# Команда /weather
@dp.message_handler(commands=['weather'])
async def cmd_weather(message: types.Message):
    args = message.get_args()
    if args:
        city = args.strip()
        await send_weather(message, city)
    else:
        await message.answer("ℹ️ Напиши: /weather Москва")

# Обработка кнопки
@dp.message_handler(lambda message: message.text == "🌤 Узнать погоду")
async def button_weather(message: types.Message):
    await message.answer("🏙 Введи название города:")

# Обработка текста (названия города)
@dp.message_handler()
async def handle_city(message: types.Message):
    if message.text.startswith('/'):
        return
    await send_weather(message, message.text)

# Функция отправки погоды
async def send_weather(message: types.Message, city: str):
    wait_msg = await message.answer(f"🔍 Ищу погоду в {city}...")
    
    weather = await get_weather(city)
    
    if weather['success']:
        text = (
            f"🌤 <b>Погода в {weather['city']}, {weather['country']}</b>\n"
            f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"🌡 Температура: {weather['temp']}°C\n"
            f"🤔 Ощущается как: {weather['feels_like']}°C\n"
            f"☁️ {weather['description'].capitalize()}\n"
            f"💧 Влажность: {weather['humidity']}%"
        )
        await wait_msg.delete()
        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_keyboard())
    else:
        await wait_msg.edit_text(
            f"❌ Город '{city}' не найден. Проверь название и попробуй снова."
        )

# Запуск бота
if __name__ == '__main__':
    logging.info("Бот запускается...")
    executor.start_polling(dp, skip_updates=True)
