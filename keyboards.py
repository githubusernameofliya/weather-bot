from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def generate_cities_list():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = KeyboardButton(text="Southampton")
    button2 = KeyboardButton(text="Winchester")
    button3 = KeyboardButton(text="Tashkent")

    keyboard.row(button1, button2)
    keyboard.row(button3)

    return keyboard