import os
import logging
import random
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
import asyncio

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера (НОВЫЙ СИНТАКСИС)
bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Инициализация планировщика
scheduler = AsyncIOScheduler(timezone=timezone('Europe/Moscow'))

# Словарь для хранения городов пользователей
user_cities = {}

# Словарь для хранения напоминаний
user_reminders = {}

# База фактов
FACTS = [
    "🤓 Сердце человека бьется около 100 000 раз в день.",
    "🤓 Колибри — единственная птица, которая может летать задом наперед.",
    "🤓 Бананы технически являются ягодами, а клубника — нет.",
    "🤓 Осьминоги имеют три сердца.",
    "🤓 Мед никогда не портится. Археологи находили мед в древних гробницах, который до сих пор съедобен.",
    "🤓 В Швейцарии запрещено заводить только одну морскую свинку, потому что они могут грустить в одиночестве.",
    "🤓 Коровы имеют лучших друзей и могут испытывать стресс, когда разлучаются с ними.",
    "🤓 Австралия длиннее, чем Луна (диаметр Луны 3400 км, Австралия — 4000 км).",
    "🤓 В Антарктиде есть ресторан, который работает только один день в году.",
    "🤓 Самый большой в мире кактус может достигать 20 метров в высоту."
]

# База анекдотов
JOKES = [
    "😂 — Дорогой, я тебе нравлюсь?\n— Да!\n— А что именно?\n— Интуиция, она меня еще ни разу не подводила!",
    "😂 Встречаются два программиста:\n— Слышал, ты женился. Ну как жена?\n— Да нормально... Интересная женщина. Вчера подходит ко мне и говорит: «Дорогой, сходи в магазин, купи хлеб, если будут яйца — возьми десяток». Я купил 10 буханок хлеба.",
    "😂 Учительница спрашивает Вовочку:\n— Вовочка, почему ты опоздал в школу?\n— Я видел сон, что побывал в 30 странах. А потом еще захотел побывать в Канаде, но меня разбудили!",
    "😂 — Доктор, я каждое утро вижу привидение!\n— А вы пробовали пить меньше?\n— Да, но привидение от этого не исчезает.",
    "😂 Сидит хакер в тюрьме. Подходит надзиратель:\n— Ты за что сидишь?\n— За взлом.\n— А чего взломал?\n— Да ничего не взломал, просто пароль забыл."
]

# База рецептов
RECIPES = {
    "борщ": "🍲 <b>Борщ</b>\n\n"
            "Ингредиенты:\n"
            "• Свекла - 2 шт\n"
            "• Капуста - 300г\n"
            "• Картофель - 4 шт\n"
            "• Морковь - 1 шт\n"
            "• Лук - 1 шт\n"
            "• Томатная паста - 2 ст.л\n"
            "• Мясо - 500г\n\n"
            "Приготовление:\n"
            "1. Сварите бульон из мяса\n"
            "2. Нарежьте овощи\n"
            "3. Обжарьте свеклу с томатной пастой\n"
            "4. Добавьте все в бульон и варите 30 мин\n"
            "5. Подавайте со сметаной",

    "блины": "🥞 <b>Блины</b>\n\n"
             "Ингредиенты:\n"
             "• Молоко - 500 мл\n"
             "• Яйца - 2 шт\n"
             "• Мука - 200 г\n"
             "• Сахар - 1 ст.л\n"
             "• Соль - щепотка\n"
             "• Масло растительное - 2 ст.л\n\n"
             "Приготовление:\n"
             "1. Смешайте яйца, сахар и соль\n"
             "2. Добавьте половину молока\n"
             "3. Постепенно всыпьте муку\n"
             "4. Влейте остальное молоко и масло\n"
             "5. Жарьте на сковороде",

    "омлет": "🍳 <b>Омлет</b>\n\n"
             "Ингредиенты:\n"
             "• Яйца - 3 шт\n"
             "• Молоко - 100 мл\n"
             "• Соль - по вкусу\n"
             "• Масло сливочное - 20 г\n\n"
             "Приготовление:\n"
             "1. Взбейте яйца с молоком и солью\n"
             "2. Разогрейте сковороду с маслом\n"
             "3. Вылейте смесь и жарьте 5-7 мин\n"
             "4. Подавайте с зеленью"
}

# База имен
BOY_NAMES = ["Александр", "Максим", "Дмитрий", "Иван", "Сергей", "Андрей", "Алексей", "Артем", "Владимир", "Михаил"]
GIRL_NAMES = ["Анна", "Мария", "Елена", "Дарья", "Ольга", "Наталья", "Екатерина", "Анастасия", "Ирина", "Татьяна"]

# Советы дня
ADVICES = [
    "💡 Высыпайтесь! 7-8 часов сна необходимы для здоровья.",
    "💡 Пейте воду. 2 литра в день помогут чувствовать себя лучше.",
    "💡 Делайте зарядку по утрам - это заряжает энергией на весь день.",
    "💡 Улыбайтесь чаще - это улучшает настроение и продлевает жизнь.",
    "💡 Читайте книги - это развивает мышление и воображение.",
    "💡 Не откладывайте на завтра то, что можно сделать сегодня.",
    "💡 Будьте благодарны за то, что имеете - это делает счастливее.",
    "💡 Окружайте себя позитивными людьми - это влияет на ваше настроение."
]

# Словарь рифм
RHYMES = {
    "кот": ["рот", "полёт", "компот", "бегемот", "самолёт"],
    "дом": ["гном", "альбом", "потом", "знаком", "мультфильм"],
    "лес": ["чудес", "завес", "повесил", "интерес", "воскрес"],
    "море": ["горе", "вскоре", "просторе", "на просторе", "форе"],
    "любовь": ["вновь", "кровь", "морковь", "бровь", "готовь"]
}

# Функция для создания клавиатуры
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🌤 Погода сейчас"))
    builder.add(KeyboardButton(text="💰 Курс валют"))
    builder.add(KeyboardButton(text="😄 Случайный факт"))
    builder.add(KeyboardButton(text="😂 Анекдот"))
    builder.add(KeyboardButton(text="📖 Гороскоп"))
    builder.add(KeyboardButton(text="🍳 Рецепт"))
    builder.add(KeyboardButton(text="👶 Генератор имен"))
    builder.add(KeyboardButton(text="💡 Совет дня"))
    builder.add(KeyboardButton(text="📝 Рифма"))
    builder.add(KeyboardButton(text="🎲 Случайное число"))
    builder.add(KeyboardButton(text="⏰ Напоминание"))
    builder.add(KeyboardButton(text="📍 Установить город"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Функция для получения фото
def get_welcome_photo():
    photos_folder = "photos"

    if not os.path.exists(photos_folder):
        logging.warning(f"Папка {photos_folder} не найдена")
        return None

    png_files = [f for f in os.listdir(photos_folder)
                 if f.lower().endswith('.png')]

    if not png_files:
        logging.warning("В папке photos нет PNG файлов")
        return None

    random_photo = random.choice(png_files)
    photo_path = os.path.join(photos_folder, random_photo)

    logging.info(f"Выбрано фото: {random_photo}")
    return FSInputFile(photo_path)

# Функция для получения курса валют
async def get_currency_rates():
    try:
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    usd = data['Valute']['USD']['Value']
                    eur = data['Valute']['EUR']['Value']
                    cny = data['Valute']['CNY']['Value']
                    return {
                        'success': True,
                        'usd': usd,
                        'eur': eur,
                        'cny': cny,
                        'date': data['Date'][:10]
                    }
                else:
                    return {'success': False, 'error': 'Ошибка получения курсов'}
    except Exception as e:
        logging.error(f"Ошибка при получении курсов валют: {e}")
        return {'success': False, 'error': 'Ошибка соединения'}

# Функция для получения гороскопа
def get_horoscope(sign: str) -> str:
    horoscopes = [
        f"♌ <b>Гороскоп для {sign.capitalize()} на сегодня:</b>\n\n"
        "Звезды говорят, что сегодня отличный день для новых начинаний. "
        "Ваша энергия будет на подъеме, так что используйте это время с умом. "
        "Возможны приятные сюрпризы от близких людей.",

        f"♌ <b>Гороскоп для {sign.capitalize()} на сегодня:</b>\n\n"
        "Сегодня лучше проявить осторожность в финансовых вопросах. "
        "Не поддавайтесь на уговоры и не принимайте поспешных решений. "
        "Вечером возможна романтическая встреча.",

        f"♌ <b>Гороскоп для {sign.capitalize()} на сегодня:</b>\n\n"
        "День благоприятен для общения и новых знакомств. "
        "Вы будете в центре внимания, так что не стесняйтесь проявлять себя. "
        "Хороший день для творчества и самореализации."
    ]
    return random.choice(horoscopes)

# Функция для получения погоды
async def get_weather(city: str, country: str = "RU") -> dict:
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        raise ValueError("WEATHER_API_KEY не найден в переменных окружения")

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': f"{city},{country}",
        'appid': api_key,
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
                        'pressure': data['main']['pressure'],
                        'wind_speed': data['wind']['speed'],
                        'description': data['weather'][0]['description'],
                        'icon': data['weather'][0]['icon']
                    }
                elif response.status == 404:
                    return {
                        'success': False,
                        'error': 'Город не найден. Проверьте название.'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Ошибка API: {response.status}'
                    }
        except Exception as e:
            logging.error(f"Ошибка при запросе погоды: {e}")
            return {
                'success': False,
                'error': 'Ошибка соединения с сервером погоды'
            }

# Функция для форматирования погоды
def format_weather_message(weather_data: dict) -> str:
    icon_map = {
        '01d': '☀️', '01n': '🌙',
        '02d': '⛅️', '02n': '☁️',
        '03d': '☁️', '03n': '☁️',
        '04d': '☁️', '04n': '☁️',
        '09d': '🌧', '09n': '🌧',
        '10d': '🌦', '10n': '🌦',
        '11d': '🌩', '11n': '🌩',
        '13d': '❄️', '13n': '❄️',
        '50d': '🌫', '50n': '🌫'
    }

    emoji = icon_map.get(weather_data['icon'], '🌡')

    message = f"{emoji} <b>Погода в {weather_data['city']}, {weather_data['country']}</b>\n"
    message += f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
    message += f"🌡 <b>Температура:</b> {weather_data['temp']:.1f}°C\n"
    message += f"🤔 <b>Ощущается как:</b> {weather_data['feels_like']:.1f}°C\n"
    message += f"☁️ <b>Описание:</b> {weather_data['description'].capitalize()}\n"
    message += f"💧 <b>Влажность:</b> {weather_data['humidity']}%\n"
    message += f"💨 <b>Ветер:</b> {weather_data['wind_speed']} м/с\n"
    message += f"📊 <b>Давление:</b> {weather_data['pressure']} гПа"

    return message

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    photo = get_welcome_photo()

    welcome_text = (
        "👋 <b>Привет! Я многофункциональный бот.</b>\n\n"
        "Я умею:\n"
        "🌤 Показывать погоду\n"
        "💰 Курсы валют\n"
        "😄 Случайные факты\n"
        "😂 Анекдоты\n"
        "📖 Гороскопы\n"
        "🍳 Рецепты\n"
        "👶 Генерировать имена\n"
        "💡 Давать советы\n"
        "📝 Подбирать рифмы\n"
        "🎲 Случайные числа\n"
        "⏰ Напоминания\n\n"
        "Выбирай кнопку или введи команду!"
    )

    if photo:
        await message.answer_photo(
            photo=photo,
            caption=welcome_text,
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            welcome_text,
            reply_markup=get_main_keyboard()
        )

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "🔍 <b>Как пользоваться ботом:</b>\n\n"
        "🌤 <b>Погода:</b> Название города или /weather Москва\n"
        "💰 <b>Курс валют:</b> /course или кнопка\n"
        "😄 <b>Случайный факт:</b> /fact или кнопка\n"
        "😂 <b>Анекдот:</b> /joke или кнопка\n"
        "📖 <b>Гороскоп:</b> /horo лев или кнопка\n"
        "🍳 <b>Рецепт:</b> /recipe борщ или кнопка\n"
        "👶 <b>Генератор имен:</b> /name м или /name ж\n"
        "💡 <b>Совет дня:</b> /advice или кнопка\n"
        "📝 <b>Рифма:</b> /rhyme кот или кнопка\n"
        "🎲 <b>Случайное число:</b> /random 1 100\n"
        "⏰ <b>Напоминание:</b> /timer 10m Напомни про чай"
    )
    await message.answer(help_text)

# Обработчик текстовых сообщений
@dp.message()
async def handle_text(message: types.Message):
    text = message.text

    if text == "💰 Курс валют":
        waiting = await message.answer("⏳ Получаю курсы валют...")
        rates = await get_currency_rates()

        if rates['success']:
            text = (
                "💰 <b>Курсы валют ЦБ РФ</b>\n"
                f"📅 {rates['date']}\n\n"
                f"🇺🇸 Доллар USD: <b>{rates['usd']:.2f} ₽</b>\n"
                f"🇪🇺 Евро EUR: <b>{rates['eur']:.2f} ₽</b>\n"
                f"🇨🇳 Юань CNY: <b>{rates['cny']:.2f} ₽</b>"
            )
            await waiting.delete()
            await message.answer(text)
        else:
            await waiting.edit_text("❌ Не удалось получить курсы валют. Попробуйте позже.")

    elif text == "😄 Случайный факт":
        await message.answer(random.choice(FACTS))

    elif text == "😂 Анекдот":
        await message.answer(random.choice(JOKES))

    elif text == "💡 Совет дня":
        await message.answer(random.choice(ADVICES))

    elif text == "📝 Рифма":
        words_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=word) for word in RHYMES.keys()]],
            resize_keyboard=True
        )
        words_keyboard.add(KeyboardButton(text="🔙 Назад"))
        await message.answer("Выберите слово:", reply_markup=words_keyboard)

    elif text == "🎲 Случайное число":
        num = random.randint(1, 100)
        await message.answer(f"🎲 Случайное число от 1 до 100: <b>{num}</b>")

    elif text == "👶 Генератор имен":
        gender_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👨 Мужское"), KeyboardButton(text="👩 Женское")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
        await message.answer("Выберите пол:", reply_markup=gender_keyboard)

    elif text == "👨 Мужское":
        await message.answer(f"👨 Мужское имя: <b>{random.choice(BOY_NAMES)}</b>", reply_markup=get_main_keyboard())

    elif text == "👩 Женское":
        await message.answer(f"👩 Женское имя: <b>{random.choice(GIRL_NAMES)}</b>", reply_markup=get_main_keyboard())

    elif text == "🍳 Рецепт":
        dishes_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=dish) for dish in RECIPES.keys()]],
            resize_keyboard=True
        )
        dishes_keyboard.add(KeyboardButton(text="🔙 Назад"))
        await message.answer("Выберите блюдо:", reply_markup=dishes_keyboard)

    elif text in RECIPES.keys():
        await message.answer(RECIPES[text], reply_markup=get_main_keyboard())

    elif text == "📖 Гороскоп":
        signs = ["Овен ♈", "Телец ♉", "Близнецы ♊", "Рак ♋", "Лев ♌", "Дева ♍",
                 "Весы ♎", "Скорпион ♏", "Стрелец ♐", "Козерог ♑", "Водолей ♒", "Рыбы ♓"]
        signs_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=sign) for sign in signs[i:i + 3]] for i in range(0, len(signs), 3)],
            resize_keyboard=True
        )
        signs_keyboard.add(KeyboardButton(text="🔙 Назад"))
        await message.answer("Выберите ваш знак зодиака:", reply_markup=signs_keyboard)

    elif any(sign in text for sign in ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
                                       "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]):
        sign = text.split()[0].lower()
        await message.answer(get_horoscope(sign), reply_markup=get_main_keyboard())

    elif text == "🔙 Назад":
        await message.answer("Главное меню:", reply_markup=get_main_keyboard())

    elif text == "🌤 Погода сейчас":
        user_id = message.from_user.id
        if user_id in user_cities:
            await send_weather(message, user_cities[user_id])
        else:
            await message.answer("📍 Сначала установите город по умолчанию через /setcity или отправьте название города")

    elif text == "📍 Установить город":
        await message.answer("🏙 Отправьте название города, который хотите установить по умолчанию")

    elif text == "ℹ️ Помощь":
        await cmd_help(message)

    elif not text.startswith('/'):
        await send_weather(message, text)

async def send_weather(message: types.Message, city: str):
    waiting_msg = await message.answer(f"🔍 Ищу погоду в <b>{city}</b>...")

    weather_data = await get_weather(city)

    if weather_data['success']:
        weather_message = format_weather_message(weather_data)
        await waiting_msg.delete()
        await message.answer(weather_message)
        user_cities[message.from_user.id] = city
    else:
        await waiting_msg.edit_text(f"❌ {weather_data['error']}")

@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        await send_weather(message, args[1].strip())
    else:
        await message.answer("ℹ️ Укажите город после команды, например: /weather Москва")

@dp.message(Command("setcity"))
async def cmd_setcity(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        city = args[1].strip()
        user_cities[message.from_user.id] = city
        await message.answer(f"✅ Город по умолчанию установлен: <b>{city}</b>")
    else:
        await message.answer("ℹ️ Укажите город после команды, например: /setcity Москва")

@dp.message(Command("course"))
async def cmd_course(message: types.Message):
    waiting = await message.answer("⏳ Получаю курсы валют...")
    rates = await get_currency_rates()

    if rates['success']:
        text = (
            "💰 <b>Курсы валют ЦБ РФ</b>\n"
            f"📅 {rates['date']}\n\n"
            f"🇺🇸 Доллар USD: <b>{rates['usd']:.2f} ₽</b>\n"
            f"🇪🇺 Евро EUR: <b>{rates['eur']:.2f} ₽</b>\n"
            f"🇨🇳 Юань CNY: <b>{rates['cny']:.2f} ₽</b>"
        )
        await waiting.delete()
        await message.answer(text)
    else:
        await waiting.edit_text("❌ Не удалось получить курсы валют. Попробуйте позже.")

@dp.message(Command("fact"))
async def cmd_fact(message: types.Message):
    await message.answer(random.choice(FACTS))

@dp.message(Command("joke"))
async def cmd_joke(message: types.Message):
    await message.answer(random.choice(JOKES))

@dp.message(Command("advice"))
async def cmd_advice(message: types.Message):
    await message.answer(random.choice(ADVICES))

@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    args = message.text.split()
    if len(args) == 3:
        try:
            min_num = int(args[1])
            max_num = int(args[2])
            if min_num < max_num:
                num = random.randint(min_num, max_num)
                await message.answer(f"🎲 Случайное число от {min_num} до {max_num}: <b>{num}</b>")
            else:
                await message.answer("❌ Минимальное число должно быть меньше максимального")
        except ValueError:
            await message.answer("❌ Использование: /random [min] [max]")
    else:
        num = random.randint(1, 100)
        await message.answer(f"🎲 Случайное число от 1 до 100: <b>{num}</b>")

@dp.message(Command("horo"))
async def cmd_horo(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        await message.answer(get_horoscope(args[1].strip().lower()))
    else:
        await message.answer("Использование: /horo [знак]\nНапример: /horo лев")

@dp.message(Command("recipe"))
async def cmd_recipe(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        dish = args[1].strip().lower()
        if dish in RECIPES:
            await message.answer(RECIPES[dish])
        else:
            await message.answer(f"❌ Рецепт '{dish}' не найден. Доступны: {', '.join(RECIPES.keys())}")
    else:
        await message.answer("Использование: /recipe [блюдо]\nНапример: /recipe борщ")

@dp.message(Command("name"))
async def cmd_name(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        gender = args[1].strip().lower()
        if gender in ['м', 'муж', 'male']:
            await message.answer(f"👨 Мужское имя: <b>{random.choice(BOY_NAMES)}</b>")
        elif gender in ['ж', 'жен', 'female']:
            await message.answer(f"👩 Женское имя: <b>{random.choice(GIRL_NAMES)}</b>")
        else:
            await message.answer("Использование: /name м (мужское) или /name ж (женское)")
    else:
        await message.answer("Использование: /name м (мужское) или /name ж (женское)")

@dp.message(Command("rhyme"))
async def cmd_rhyme(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        word = args[1].strip().lower()
        if word in RHYMES:
            rhymes_list = ", ".join(RHYMES[word])
            await message.answer(f"📝 Рифмы к слову <b>{word}</b>:\n{rhymes_list}")
        else:
            await message.answer(f"❌ Рифмы к слову '{word}' не найдены")
    else:
        await message.answer("Использование: /rhyme [слово]\nНапример: /rhyme кот")

async def send_daily_weather():
    if not user_cities:
        logging.info("Нет пользователей для ежедневной рассылки")
        return

    default_city = os.getenv('DEFAULT_CITY', 'Moscow')
    default_country = os.getenv('DEFAULT_COUNTRY', 'RU')

    weather_data = await get_weather(default_city, default_country)

    if weather_data['success']:
        weather_message = format_weather_message(weather_data)
        weather_message = "🌅 <b>Доброе утро! Погода на сегодня:</b>\n\n" + weather_message

        for user_id in user_cities.keys():
            try:
                await bot.send_message(user_id, weather_message)
                logging.info(f"Отправлена ежедневная погода пользователю {user_id}")
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    else:
        logging.error("Не удалось получить погоду для ежедневной рассылки")

async def main():
    if os.path.exists("photos"):
        png_count = len([f for f in os.listdir("photos") if f.lower().endswith('.png')])
        logging.info(f"Найдено PNG фото в папке photos: {png_count}")
    else:
        logging.warning("Папка 'photos' не найдена. Создайте её и добавьте PNG фото.")

    scheduler.add_job(send_daily_weather, 'cron', hour=8, minute=0)
    scheduler.start()
    logging.info("Планировщик запущен. Ежедневная рассылка в 8:00")

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.info("Бот запускается...")
    asyncio.run(main())