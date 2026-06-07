import telebot
import requests
from telebot import types


token = '8504616493:AAEThgTZFNPtAEgrCdmiGg23CIKEdJ1tfUo'
money_exchange_api_key = 'cc7f0c232c8da8876edbd1e9'

bot = telebot.TeleBot(token)

user_states = {}


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Convert")
    return keyboard

def get_rate(base, target):
    url = f'https://v6.exchangerate-api.com/v6/{money_exchange_api_key}/latest/{base}'
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()['conversion_rates'].get(target)

def start(message):
    bot.send_message(
        message.chat.id,
        "Привет \nНажми кнопку Convert",
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Бот конвертирует валюты по актуальному курсу.\n"
        "Нажми Convert и следуй инструкциям."
    )

@bot.message_handler(func=lambda m: m.text == "Convert")
def start_convert(message):
    user_states[message.chat.id] = {"step": "amount"}
    bot.send_message(message.chat.id, "Введи сумму:")


@bot.message_handler(func=lambda m: m.chat.id in user_states)
def convert_steps(message):
    state = user_states[message.chat.id]

    if state["step"] == "amount":
        try:
            state["amount"] = float(message.text)
            state["step"] = "base"
            bot.send_message(message.chat.id, "Из какой валюты? (USD, EUR...)")
        except ValueError:
            bot.send_message(message.chat.id, "Введи число")

    elif state["step"] == "base":
        state["base"] = message.text.upper()
        state["step"] = "target"
        bot.send_message(message.chat.id, "В какую валюту?")

    elif state["step"] == "target":
        target = message.text.upper()
        rate = get_rate(state["base"], target)

        if not rate:
            bot.send_message(message.chat.id, "Неверная валюта")
            return

        result = state["amount"] * rate
        bot.send_message(
            message.chat.id,
            f"{state['amount']} {state['base']} = {round(result, 2)} {target}",
            reply_markup=main_keyboard()
        )

        del user_states[message.chat.id]


@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "Нажми кнопку Convert ", reply_markup=main_keyboard())

bot.polling()