#IMPORTS
import requests
import shelve
import json
from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

#CONSTANTS
USERS_PATH = '/home/yournightmare/bot/users'
MAIN_PATH = '/home/yournightmare/bot/'
BOT_TOKEN = 'BOT-TOKEN'
URL='https://api.telegram.org/' + BOT_TOKEN
MESSAGE_URL = URL + 'sendMessage'
KEYS_NAME = {
    'name': 'ФИО',
    'city': 'Город',
    'age':  'Возраст',
    'market':'Откуда узнали о нас',
    'username':'Username',
}
PATHS = {
    'name': '/home/yournightmare/bot/name',
    'city': '/home/yournightmare/bot/city',
    'age': '/home/yournightmare/bot/age',
    'market': '/home/yournightmare/bot/market',
    'phone': '/home/yournightmare/bot/phone',
    }
MESSAGES_STORE = {
    '2': {  'text': 'Выберите свой город!',
            'buttons': {'keyboard': [['Усть-Каменогорск'],['Павлодар'],['Алматы'],['Астана(Нур-Султан)']], 'resize_keyboard': True, 'one_time_keyboard': True},},
    '3': {  'text': 'Откуда узнали о нас?',
            'buttons': {'keyboard': [['OLX'],['Вконтакте'],['MarketKZ']], 'resize_keyboard': True, 'one_time_keyboard': True},},
    '4': {  'text': 'Напишите свой возраст!',
            'buttons': None,},
    '5': {  'text': 'Напишите свои ФИО!',
            'buttons': None,},
    '6': {  'text': 'Напишите свой номер телефона!',
            'buttons': None,},
    '7': {  'text': 'Спасибо за оставленную заявку! В течение суток с Вами свяжется менеджер Вашего города.',
            'buttons': None,},
    'start': { 'text': 'Аутсорсинговая компания LIGHTWORK примет на работу грузчиков-разнорабочих.\n\nМы занимаемся предоставлением услуг грузчиков и разнорабочих.\n\nРаботаем по заказам\n- Коммерческим\n- Бытовым\n- Промышленным.\n\nВы должны быть:\n- Ответственным\n- Пунктуальным\n- Сообразительным\n- Внимательны.\n- Умеете оперативно давать отклики в вацапе и отвечать на вопросы руководства. ( максимум в течении 5 минут )\n- У вас должен быть Вацап\n- У вас всегда под рукой телефон\n- Вы трудолюбивый человек.\n- Готовы ездить на 3-4 заказа в день\n- Уметь строго соблюдать регламент\n\nМы предлагаем:\n- Работу с гибким графиком\n- Разнообразная деятельность\n- Дружный коллектив\n- Хорошую заработную плату 1000 тенге в час\n- Возможность карьерного роста\n- Оплата сразу после заказа.\n- Стабильный растущий приток заказов от 2-12 заказов в день.\n- Премии 10.000 тг и выше\n- Постоянную занятость и доход до 10.000 тг в день.\n- Средний заработок 5-6 тысяч в день\n\nС нами возможно зарабатывать до 178.000 тг в месяц.',
                'buttons': {'keyboard': [['Оставить заявку'],['Нет, спасибо']], 'resize_keyboard': True, 'one_time_keyboard': True},},
    }

#FUNCTIONS
def step_reducer(chat_id, action):
    key = str(chat_id)
    with shelve.open(USERS_PATH) as users:
        if (action == "return"):
            if key in users:
                step = users[key]
                return step
            else:
                step = 1
                users[key] = str(step)
                return step

        elif action == "wrong":
            users[key] = str(int(users[key])-1)

        elif action == "reset":
            users[key] = '1'

        elif action == "add":
            users[key] = str(int(users[key])+1)

def message_reducer(chat_id, key):
    send_message(chat_id,
        MESSAGES_STORE[str(key)]["text"],
        MESSAGES_STORE[str(key)]["buttons"])

def send_report(chat_id, username):
    output = username + "\n"
    for i in PATHS:
        with shelve.open(PATHS[i]) as data:
            text = str(data[str(chat_id)])
            output += KEYS_NAME[i] + ": " + text + "\n"
    #SEND REPORT IN MY CHAT
    send_message('884406200', output)

def write(chat_id, action, message):
    with shelve.open(PATHS[action]) as file:
        key = str(chat_id)
        msg = str(message)
        (file[key]) = msg

def send_message(chat_id, text, reply_markup=None):
    if reply_markup == None:
        answer = {'chat_id': chat_id, 'text': text}
    else:
        reply_markup = json.dumps(reply_markup)
        answer = {'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup}
    r = requests.post(MESSAGE_URL, json=answer)
    return r.json()

#APP
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        chat_id = r['message']['chat']['id']
        username = r['message']['chat']['first_name']
        try:
            message = r['message']["text"]
            step = int(step_reducer(chat_id, 'return'))
            if (step == 1) and ('start' in message):
                step_reducer(chat_id, 'add')
                message_reducer(chat_id, 'start')

            elif not(step == 1) and ('start' in message):
                step_reducer(chat_id, 'reset')
                message_reducer(chat_id, 'start')

            elif (step == 2) and ('Оставить заявку' in message):
                message_reducer(chat_id, step)

            elif (step == 2) and ('Нет, спасибо' in message):
                text = 'Чтобы снова запустить бота отправьте /start'
                send_message(chat_id, text)
                step_reducer(chat_id, 'wrong')

            elif (step == 3):
                write(chat_id, "city", message)
                message_reducer(chat_id, step)

            elif (step == 4):
                write(chat_id, "market", message)
                message_reducer(chat_id, step)

            elif (step == 5):
                write(chat_id, "age", message)
                message_reducer(chat_id, step)

            elif (step == 6):
                write(chat_id, "name", message)
                message_reducer(chat_id, step)

            elif (step == 7):
                write(chat_id, "phone", message)
                send_report(chat_id, username)
                message_reducer(chat_id, step)

            elif ('chat_id' in message):
                step_reducer(chat_id, 'wrong')
                text = str(chat_id)
                send_message(chat_id, text)

            else:
                step_reducer(chat_id, 'wrong')
                text = 'Неизвестная команда.\nЧтобы снова запустить бота отправьте /start'
                send_message(chat_id, text)

            step_reducer(chat_id, 'add')
        except:
            text = 'Error'
            send_message(chat_id, text)

        return jsonify(r)
    return '<h1>Bot is running</h1>'
if __name__ == '__main__':
    app.run()
