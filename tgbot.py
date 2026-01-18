import telebot, schedule, time, threading
import requests
import math
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, date
from flask import Flask

TOKEN = '8217201077:AAFm1TPWmPdidpLlL0pKEwNidQhR1n8FkZc'

# weather api info 
WEATHER_API = '39ea2186132e627690537b853861ebf2'
CITY = 'Brest'
COUNTRY_CODE = 'BY'

counter = 0

# SERVER
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot in running 🚀'

def run_bot():
    app.run(host='0.0.0.0', port=3000)

threading.Thread(target=run_bot).start()


def help():
    return f''' 
Добро пожаловать в бота VPBot 👋
При помощи этого бота вы можете каждый день 
получать  актуальную информацию 📰
Этот бот самостоятельно вам напишет ее, 
если вы этого захотите 😉 
Для работы с нашим тг ботом вы можете воспользоваться меню,
которое расположено ниже ⬇️

P.S | Если у вас возникли проблемы, которые вы не можете решить...
Обращайтесь к администратору нашего бота @wovkess 
'''

def getCurrency():
    CURRENCY_URL = 'https://api.nbrb.by/exrates/rates?periodicity=0'
    response = requests.get(CURRENCY_URL)
    data = response.json()

    now = datetime.now()
    day = now.strftime("%d.%m.%Y")
    
    for item in data:
        if item['Cur_Abbreviation'] == 'USD':
            usdObj = item
        elif item['Cur_Abbreviation'] == 'EUR':
            eurObj = item
        elif item['Cur_Abbreviation'] == 'RUB':
            rubObj = item
        elif item['Cur_Abbreviation'] == 'PLN':
            plnObj = item
        elif item['Cur_Abbreviation'] == 'AED':
            aedObj = item
    return f'''
💰 Курс валюты на {day}

🇺🇸 {usdObj['Cur_Scale']} USD = 🇧🇾 {usdObj['Cur_OfficialRate']} BYN
🇪🇺 {eurObj['Cur_Scale']} EUR = 🇧🇾 {eurObj['Cur_OfficialRate']} BYN
🇷🇺 {rubObj['Cur_Scale']} RUB = 🇧🇾 {rubObj['Cur_OfficialRate']} BYN
🇵🇱 {plnObj['Cur_Scale']} PLB = 🇧🇾 {plnObj['Cur_OfficialRate']} BYN
🇦🇪 {aedObj['Cur_Scale']} AED = 🇧🇾 {aedObj['Cur_OfficialRate']} BYN
'''

def getWeather():
    WEATHER_URL = f'https://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY_CODE}&appid={WEATHER_API}'

    try:
        response = requests.get(WEATHER_URL)
        data = response.json()
        temp = round(data['main']['temp'] - 273)
        desc = data['weather'][0]['description']
        feels = round(data['main']['feels_like'] - 273)
        wind_speed = data['wind']['speed']
        humidity = data['main']['humidity']
        if temp <= 4:
            tempMsg = 'потеплее🥶'
        elif temp > 4 and temp <= 21:
            tempMsg = 'полегче🧥'
        else: 
            tempMsg = 'легко👚'
        
        if humidity >= 80:
            humMsg = 'Возьми с собой шапку и шарфик 🧢🧣. '
        else:
            humMsg = ''

        if wind_speed >= 5:
            windMsg = 'Сегодня ожидается сильный ветер, будь более устойчивый 🐘'
        else: 
            windMsg = 'Сегодня слабый ветер, расслабься 🧚'

        return f'''
⛅ Погода в {CITY}, {COUNTRY_CODE}
ℹ️ {desc}
🌡️ Температура: {temp}°С 
😇 Ощущается как: {feels}°С
💧 Влажность: {humidity}%
🍃 Скорость ветра:  {wind_speed} м/c
Сегодня советую одеться {tempMsg}.
{windMsg}
{humMsg}
'''

    except Exception as error:
        return f'Ошибка получения погоды {error}'

bot = telebot.TeleBot(TOKEN)

adminChatId = 768655230

userChatIds = []

weather_counter = 0

# меню программы

def main_menu(message):
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton('Подписаться на рассылку 📬')
    btn2 = KeyboardButton('Узнать погоду ⛅')
    btn5 = KeyboardButton('Узнать курс валют 💹')
    btn3 = KeyboardButton('Помощь ❓')
    btn4 = KeyboardButton('Отписаться от рассылки ❌')
    btn6 = KeyboardButton('👨‍🦰Администратор')
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn5)
    menu.add(btn3)
    menu.add(btn4)
    if message.chat.id == adminChatId:
        menu.add(btn6)
    return menu

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name} 👋\nВыберите нужную команду: ', reply_markup=main_menu(message))
    bot.send_sticker(message.chat.id, 'CAACAgQAAxkBAAEBv41pEEdLy_0AAaB3gsM2NGbF-ssc3HsAAs4QAALF8RBRDvUHfs1FA0A2BA')
    print(message.chat.id)


def stats(message):
    if adminChatId == message.chat.id:
        bot.reply_to(message, f'''
📊Статистика бота

👤Количество подписчиков: {len(userChatIds)}
🔢Количество запросов погоды: {weather_counter} 
''')
    else: 
        bot.reply_to(message, 'Вы не администратор бота!')

# обработчик кнопок меню
@bot.message_handler(func=lambda message: True)
def listen_all(message):
    text = message.text

    global weather_counter

    if text == 'Подписаться на рассылку 📬':
        userChatId = message.chat.id
        bot.send_message(userChatId, 'Вы добавлены в список автоматической отправки писем.')
        if userChatId not in userChatIds:
            userChatIds.append(userChatId)
    elif text == 'Узнать погоду ⛅':
        bot.reply_to(message, getWeather())
        weather_counter += 1
    elif text == 'Узнать курс валют 💹':
        bot.reply_to(message, getCurrency())
    elif text == 'Помощь ❓':
        bot.reply_to(message, help())
    elif text == 'Отписаться от рассылки ❌':
        userChatId = message.chat.id
        if userChatId in userChatIds:
            bot.send_message(userChatId, 'Вы отписались от рассылки 🫡')
            userChatIds.remove(userChatId)
        else: 
            bot.send_message(userChatId, 'Вы не были подписаны на рассылку 🙃')
    elif text == '👨‍🦰Администратор':
        stats(message)
    else:
        bot.reply_to(message, 'Увы... Такой команды нет 😔')

def schedule_message():
    for id in userChatIds:
        bot.send_message(id, 'Доброе утро, босс!')
        bot.send_message(id, getWeather())
        bot.send_message(id, getCurrency())

# функция для проверки времени
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(5)

schedule.every().day.at("10:22").do(schedule_message)

# второй поток программы
threading.Thread(target = schedule_checker, daemon=True).start()

# start bot 

print('Bot started 🚀')
bot.polling(none_stop=True)
