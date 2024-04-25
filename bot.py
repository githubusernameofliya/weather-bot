from datetime import datetime
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from pymysql import connect
from requests import get
from aiogram.types import ReplyKeyboardRemove

from keyboards import generate_cities_list, generate_save_city_button

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

def fetch_cities(user):
    cursor.execute("""SELECT * FROM cities WHERE user_id = %s""", (user[0],))
    cities = cursor.fetchall()
    return cities


@dp.message_handler(commands='start')
async def say_hello(message: Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name

    
    cursor.execute("""SELECT * FROM users WHERE user_id = %s""", (telegram_id,))
    user = cursor.fetchone()

    
    cities = fetch_cities(user)

    # TODO: Cities list is not updated automatically on every start, needs to be fixed
    

    if not user:
        cursor.execute(
            """INSERT INTO users(full_name, user_id) VALUES (%s, %s)""", (full_name, telegram_id))
        connection.commit()
        await bot.send_message(chat_id=telegram_id, text="We are glad to seee you there !", reply_markup=generate_cities_list())

    else:
        await bot.send_message(chat_id=telegram_id, text="Welcome back !",  reply_markup=generate_cities_list(cities))


@dp.message_handler(commands='clear')
async def clear_cities_list(message: Message):
    telegram_id = message.from_user.id
    
    # Identify user id by telegram id from users table
    cursor.execute("""SELECT * FROM users WHERE user_id = %s""", (telegram_id,))
    user = cursor.fetchone()
    
    # Clear cities list of this user from cities table
    cursor.execute("""DELETE FROM cities WHERE user_id = %s""", (user[0],))
    connection.commit()
    
    # Update cities list for this user
    cities = fetch_cities(user=user)

    # Inform user about this operation
    await bot.send_message(chat_id=telegram_id,
                           text="Your cities list has bees successfully cleaned",
                           reply_markup=ReplyKeyboardRemove())



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
        desc = data["weather"][0]["description"].capitalize()
        wind_speed = data["wind"]["speed"]
        # sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%m")
        # sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%m")
        # timezone = data["timezone"]  # 18000 => 5 hours

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
        # Sunrise: {sunrise}
        # Sunset: {sunset}
        # Timezone: {timezone // 3600} hour(s) 
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=generate_save_city_button(city_name=message.text.capitalize()))

    except:
        await bot.send_message(chat_id=chat_id, text="Invalid city name")


@dp.callback_query_handler()
async def save_city_to_cities_list(callback: CallbackQuery):

    #
    city_name = callback.data

    
    telegram_id = callback.from_user.id
    
    
    cursor.execute("""SELECT id FROM users WHERE user_id = %s""", (telegram_id,))
    user_id = cursor.fetchone()

    
    cursor.execute("""SELECT * FROM cities WHERE user_id = %s AND city_name = %s""", (user_id, city_name))
    city = cursor.fetchone()

    if not city:
        
        cursor.execute("""INSERT INTO cities (user_id, city_name) VALUES (%s, %s)""", 
                       (user_id, city_name))
        connection.commit()

        
        cities = fetch_cities(user=(user_id, ""))

        
        await bot.send_message(chat_id=telegram_id, 
                           text=f"{city_name} was saved successfully", 
                           reply_markup=generate_cities_list(cities))
    
    else:
        
        await bot.send_message(chat_id=telegram_id,
                               text=f"You already have {city_name} in your cities list")

executor.start_polling(dispatcher=dp)
