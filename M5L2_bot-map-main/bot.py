import os
import tempfile
import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

def send_map(chat_id, cities, caption):
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = os.path.join(tmp_dir, 'map.png')
        manager.create_graph(path, cities)
        with open(path, 'rb') as photo:
            bot.send_photo(chat_id, photo, caption=caption)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, (
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - список команд\n"
        "/show_city <город> - показать город на карте\n"
        "/remember_city <город> - сохранить город в свой список\n"
        "/show_my_cities - показать на карте все сохранённые города\n\n"
        "Названия городов нужно писать на английском, например: /show_city London"
    ))


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, 'Укажи город после команды, например: /show_city London')
        return
    city_name = parts[1].strip()
    if manager.get_coordinates(city_name) is None:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')
        return
    send_map(message.chat.id, [city_name], city_name)


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if not cities:
        bot.send_message(message.chat.id, 'У тебя пока нет сохранённых городов. Добавь их командой /remember_city <город>')
        return
    send_map(message.chat.id, cities, 'Твои города: ' + ', '.join(cities))


if __name__=="__main__":
    manager = DB_Map(DATABASE)
    manager.create_user_table()
    bot.polling()
