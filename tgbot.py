import telebot
import schedule
import time
import threading
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton 
from datetime import datetime, date

TOKEN = '8217201077:AAFm1TPWmPdidpLlL0pKEwNidQhR1n8FkZc'

# weather api info
WEATHER_API = 'd1db92c2093eb93ff11ade9e249eed9d'
CITY = 'Brest'
COUNTRY_CODE = 'BY'


def help():
    return f'''
Добро пожаловать в NyahBOT 👋

-------------------------------------
При помощи этого бота вы можете каждый день получать
актуальную информацию.
-------------------------------------

Этот бот может дать:
-❗Информацию о погоде.
-❗Информацию о валютах.
-❗Нажав на "Подписаться на рассылку 📨" вы
можете получать информацию каждый день! 😊

-------------------------------------
P.S | По поводу всех вопросов обращаться к @ssweetsswift
'''

def getCurrency():
    CURRENCY_URL = ' https://api.nbrb.by/exrates/rates?periodicity=0'
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
    return f'''
🏦Курс валюты на {day}.
-------------------------------------
🇺🇸 {usdObj['Cur_Scale']} USD = 🇧🇾 {usdObj['Cur_OfficialRate']} BYN.
🇪🇺 {eurObj['Cur_Scale']} EUR = 🇧🇾 {eurObj['Cur_OfficialRate']} BYN.
🇷🇺 {rubObj['Cur_Scale']} RUB = 🇧🇾 {rubObj['Cur_OfficialRate']} BYN.
🇵🇱 {plnObj['Cur_Scale']} PLN = 🇧🇾 {plnObj['Cur_OfficialRate']} BYN.
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
            tempMsg = 'теплее ❄️'
        elif temp > 4 and temp <= 21:
            tempMsg = 'полегче 🧥'
        else:
            tempMsg = 'легко 👕'
        
        if humidity >= 80:
            humMsg = 'Возьми с собой шарфик! 🧣'
        else:
            humMsg = ''
        
        if wind_speed >= 5:
            windMsg = 'Сегодня сильный ветер, держись крепче! 🌬️'
        else:
            windMsg = ''
        return f''' 
⛅ Погода в {CITY}, {COUNTRY_CODE}.
-------------------------------------
❁ {desc}.
🌡️ Температура: {temp}°C 
🤔 Ощущается как: {feels}°C
☔ Влажность: {humidity}%
🌪️ Скорость ветра: {wind_speed} м/с
-------------------------------------
Сегодня советую одеться {tempMsg}
{windMsg}
{humMsg}
'''
    except Exception as error:
        return f'Ошибка получения погоды {error}.'

bot = telebot.TeleBot(TOKEN)

adminChatId = 1671752119

userChatIds = []

weather_counter = 0

# Меню

def main_menu(message):
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton('Подписаться на рассылку 📨')
    btn2 = KeyboardButton('Узнать погоду ⛅')
    btn3 = KeyboardButton('Узнать курс валют 💱')
    btn4 = KeyboardButton('Помощь 🙏')
    btn5 = KeyboardButton('Отписаться от рассылки 👋')
    btn6 = KeyboardButton('Администратор 🔐')
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)
    menu.add(btn4)
    menu.add(btn5)
    if message.chat.id == adminChatId:
        menu.add(btn6)
    return menu

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name}! \nВыберите нужную команду: ', reply_markup=main_menu(message))
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBv5JpEEdkwOBWIw-Pp2z0kUHj1A18lAACmjYAAoe_qEkI1g6hsqfk-TYE')
    print(message.chat.id)

def stats(message):
    if adminChatId == message.chat.id:
        bot.reply_to(message, f'''
📊 Статистика бота
-------------------------------------
👥 Количество подписчиков: {len(userChatIds)}
🔢 Количество запросов погоды: {weather_counter}
''')
    else:
        bot.reply_to(message, 'У вас нет прав на использование этой команды.')

# Обработка сообщений и кнопок меню
@bot.message_handler(func = lambda  message: True)
def listen_all(message):
    text = message.text
    global weather_counter
    if (text) == 'Подписаться на рассылку 📨':
        userChatId = message.chat.id
        bot.send_message(userChatId, 'Теперь Вы будете получать сообщения каждый день')
        if userChatId not in userChatIds:
            userChatIds.append(userChatId)
    elif text == 'Узнать погоду ⛅':
        bot.reply_to(message, getWeather())
        weather_counter += 1
    elif text == 'Узнать курс валют 💱':
        bot.reply_to(message, getCurrency())
    elif text == 'Помощь 🙏':
        bot.reply_to(message, help())
    elif text == 'Отписаться от рассылки 👋':
        userChatId = message.chat.id
        if userChatId in userChatIds:
            bot.send_message(userChatId, 'Вы больше не будете получать сообщения каждый день 😓')
            userChatIds.remove(userChatId)
        else:
            bot.send_message(userChatId, 'Вы не были подписаны на рассылку 😶‍🌫️')
    elif text == 'Администратор 🔐':
        stats(message)
    else:
        bot.reply_to(message, 'Ошибка! Такой команды нет.. 😥')

def schedule_message():
    for id in userChatIds:
        bot.send_message(id, 'Доброе утро, Sweeta!')
        bot.send_message(id, getWeather())
        bot.send_message(id, getCurrency())
        


# Проверка времени
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(10)

schedule.every().day.at("06:00").do(schedule_message)

#Второй поток
threading.Thread(target = schedule_checker, daemon = True).start()


bot.polling()