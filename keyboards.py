from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton # Inline buttons => attached to message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def generate_cities_list(cities = []):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)


    in_row = 2
    start = 0
    end = in_row
    rows = len(cities) // in_row

    if len(cities) % in_row != 0:
        rows += 1
    
    for _ in range(rows):
        buttons = []
        for city_id, user_id, city_name in cities[start:end]:
            buttons.append(
                KeyboardButton(text=city_name)
            )
        keyboard.row(*buttons)
        start = end
        end += in_row

    return keyboard


def generate_save_city_button(city_name):
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text=f"Save {city_name}", callback_data=city_name)
    keyboard.add(button)

    return keyboard
