import telebot
import requests
from telebot import types
from difflib import get_close_matches
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


token = '8504616493:AAEThgTZFNPtAEgrCdmiGg23CIKEdJ1tfUo'
weather_api_key = 'bc50eded1a9c42d5b08140442261801'

bot = telebot.TeleBot(token)

CITIES = [
    # --- Asia ---
    "Tokyo", "Seoul", "Beijing", "Shanghai", "Hong Kong", "Taipei",
    "Bangkok", "Hanoi", "Jakarta", "Manila", "Kuala Lumpur", "Singapore",
    "New Delhi", "Mumbai", "Dhaka", "Islamabad", "Karachi",
    "Astana", "Almaty", "Tashkent", "Bishkek", "Dushanbe",
    "Tehran", "Baghdad", "Riyadh", "Doha", "Abu Dhabi", "Dubai",
    "Jerusalem", "Tel Aviv", "Amman", "Beirut",
    "Ulaanbaatar", "Pyongyang",

    # --- Europe ---
    "London", "Paris", "Berlin", "Madrid", "Rome", "Milan",
    "Vienna", "Prague", "Warsaw", "Budapest",
    "Brussels", "Amsterdam", "Luxembourg",
    "Copenhagen", "Oslo", "Stockholm", "Helsinki",
    "Dublin", "Edinburgh",
    "Lisbon", "Athens",
    "Zurich", "Geneva",
    "Moscow", "Saint Petersburg", "Kyiv", "Minsk",
    "Bucharest", "Sofia", "Belgrade",
    "Zagreb", "Ljubljana", "Sarajevo", "Skopje",
    "Tirana", "Podgorica",
    "Reykjavik",

    # --- Africa ---
    "Cairo", "Alexandria",
    "Tripoli", "Tunis", "Algiers", "Rabat", "Casablanca",
    "Lagos", "Abuja",
    "Accra",
    "Nairobi", "Mombasa",
    "Addis Ababa",
    "Khartoum",
    "Kampala",
    "Dar es Salaam",
    "Pretoria", "Cape Town", "Johannesburg",

    # --- North America ---
    "Washington", "New York", "Los Angeles", "Chicago",
    "Toronto", "Vancouver", "Montreal",
    "Ottawa",
    "Mexico City", "Guadalajara",
    "Havana",

    # --- South America ---
    "Brasilia", "Sao Paulo", "Rio de Janeiro",
    "Buenos Aires", "Cordoba",
    "Santiago",
    "Lima",
    "Bogota", "Medellin",
    "Caracas",
    "Montevideo",
    "Asuncion",
    "La Paz", "Sucre",
    "Quito",
    "Panama City",

    # --- Oceania ---
    "Canberra", "Sydney", "Melbourne",
    "Auckland", "Wellington",
    "Suva",

    # --- Extra world megacities ---
    "Istanbul", "Los Angeles", "San Francisco",
    "Las Vegas", "Miami",
    "Barcelona", "Munich",
    "Frankfurt",
    "Naples",
    "Osaka",
    "Busan",
    "Shenzhen",
    "Guangzhou"
]

def city_keyboard(city):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🌤 Сегодня", callback_data=f"today:{city}"),
        InlineKeyboardButton("📆 Прогноз", callback_data=f"forecast:{city}")
    )
    return keyboard

def get_weather(city):
    try:
        url = f"https://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&aqi=no"
        response = requests.get(url, timeout=5)
        data = response.json()

        if "error" in data:
            suggestions = suggest_city(city)
            if suggestions:
                return (
                    "!Город не найден!.\n"
                    "?Вы имели в виду?:\n" +
                    "\n".join(f"• {c}" for c in suggestions)
                )
            return "❌ Город не найден. Проверьте написание."

        location = data["location"]["name"]
        country = data["location"]["country"]
        current = data["current"]

        return (
            f"🌍 {location}, {country}\n"
            f"🌤 Погода: {current['condition']['text']}\n"
            f"🌡 Температура: {current['temp_c']}°C\n"
            f"💧 Влажность: {current['humidity']}%\n"
            f"💨 Ветер: {current['wind_kph']} км/ч"
        )

    except requests.exceptions.RequestException:
        return "!! Ошибка соединения с погодным сервером !!"

def suggest_city(city):
    return get_close_matches(city, CITIES, n=3, cutoff=0.6)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        '👋 Введи название города, и я скажу погоду'
    )

def start(message):
    bot.reply_to(message, "👋 Введи название города")

@bot.message_handler(func=lambda message: True)
def handle_city(message):
    city = message.text.strip()
    weather = get_weather(city)

    bot.send_message(
        message.chat.id,
        weather,
        reply_markup=city_keyboard(city)
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("weather:"))
def callback_weather(call):
    city = call.data.split(":", 1)[1]
    weather = get_weather(city)

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        weather,
        reply_markup=city_keyboard(city)
    )

def get_forecast(city, days=3):
    try:
        url = (
            f"https://api.weatherapi.com/v1/forecast.json"
            f"?key={weather_api_key}&q={city}&days={days}&aqi=no&alerts=no"
        )
        data = requests.get(url, timeout=5).json()

        if "error" in data:
            suggestions = suggest_city(city)
            if suggestions:
                return (
                    "❌ Город не найден.\n"
                    "🤔 Вы имели в виду:\n" +
                    "\n".join(f"• {c}" for c in suggestions)
                )
            return "❌ Город не найден."

        location = data["location"]["name"]
        country = data["location"]["country"]

        text = f"📍 {location}, {country}\n\n"

        for day in data["forecast"]["forecastday"]:
            date = day["date"]
            cond = day["day"]["condition"]["text"]
            max_t = day["day"]["maxtemp_c"]
            min_t = day["day"]["mintemp_c"]
            rain = day["day"]["daily_chance_of_rain"]

            text += (
                f"📅 {date}\n"
                f"🌤 {cond}\n"
                f"🌡 {min_t}°C — {max_t}°C\n"
                f"🌧 Осадки: {rain}%\n\n"
            )

        return text

    except requests.exceptions.RequestException:
        return "Ошибка соединения с сервером прогноза"

@bot.callback_query_handler(func=lambda call: call.data.startswith("forecast:"))
def callback_forecast(call):
    city = call.data.split(":", 1)[1]
    forecast = get_forecast(city, days=3)

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        forecast,
        reply_markup=city_keyboard(city)
    )

bot.polling()