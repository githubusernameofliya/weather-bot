# from aiogram import Bot, Dispatcher, executor
# from aiogram.dispatcher.filters import Text

# bot = Bot(token="7191580316:AAGdFwvL-oVzFwsSbtQzlblJ0C7kbILCgAI")

# dp = Dispatcher(bot=bot)

# @dp.message_handler(commands='start')
# async def say_hello(message):

#     chat_id = message.from_user.id
#     text = "Hello, how are you ?"

#     await bot.send_message(chat_id=chat_id, text=text)


# @dp.message_handler(Text(equals="What is your name ?"))
# async def introduce(message):
#     chat_id = message.from_user.id
#     text = "I'm the first telegram bot developed by Liya"
#     await bot.send_message(chat_id=chat_id, text=text)


# @dp.message_handler(Text(equals="Where are you from ?"))
# async def introduce(message):
#     chat_id = message.from_user.id
#     text = "I'm from Southampton,England"
#     await bot.send_message(chat_id=chat_id, text=text)


# executor.start_polling(dispatcher=dp)
from datetime import datetime
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from pymysql import connect
from requests import get

API_KEY = "98943b3a7c43ba4865aaa7f64ff282e1"
URL = "https://api.openweathermap.org/data/2.5/weather"
bot = Bot(token="7191580316:AAGdFwvL-oVzFwsSbtQzlblJ0C7kbILCgAI")
dp = Dispatcher(bot=bot)

connection = connect(
    database="railway",
    user="root",
    password="tbkCVpXPTHxsOEnAgyguwJqUufGmlBWX",
    port=19164,
    host="roundhouse.proxy.rlwy.net",
)
cursor = connection.cursor()

@dp.message_handler(commands='start')
async def say_hello(message: Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name

    cursor.execute("""SELECT * FROM users WHERE user_id = %s""", (telegram_id))
    user = cursor.fetchone()

    if not user:
        cursor.execute("""INSERT INTO users(full_name, user_id) VALUES (%s, %s)""", (full_name, telegram_id))
        connection.commit()
        await bot.send_message(chat_id=telegram_id, text="We are glad to seee you there !")

    else:
        await bot.send_message(chat_id=telegram_id, text="Welcome back !")
    
    await bot.send_message(chat_id=telegram_id, text="Type city name to find out weather informtion here.")


@dp.message_handler()
async def answer_weather_data(message: Message):
    chat_id = message.from_user.id

    
    try:
        PARAMS = {
            'q': message.text,
            'appid': API_KEY,
            'units': 'metric',
        }
        response = get(url=URL, params=PARAMS)
        data = response.json()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        desc = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%m")
        sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%m")



        text = f"""🏙 Today in <b>{message.text}</b>
        
🌞Temperature: <b>{temp} C°</b>
☀️ Feels like: <b>{feels_like} C°</b>
❄️ Min. temperature: <b>{temp_min} C°</b>
🔥 Max. temperature: <b>{temp_max} C°</b>

💧 Humidity: <b>{humidity}%</b>
🎯 Pressure: <b>{pressure} Pa</b>
📃 Description: <b>{desc}</b>
💨 Wind speed: <b>{wind_speed} km/h</b>
"""

        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
  
    except:
        await bot.send_message(chat_id=chat_id, text="Invalid city name.")

executor.start_polling(dispatcher=dp)