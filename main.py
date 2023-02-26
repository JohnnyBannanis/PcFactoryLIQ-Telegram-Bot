import requests
import time, threading, schedule
import telebot
import private
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


API_KEY = private.API_KEY
BASE_URL = private.BASE_URL

bot = telebot.TeleBot(API_KEY)
subscribed = []


commands = {  # command description used in the "help" command
    'start'         : 'Get used to the bot',
    'help'          : 'Gives you information about the available commands',
    'ping'          : 'Gives a Pong reply if the bot is running',
    'categories'    : 'Display the current categories of products available',
    'subscribe'     : 'Adds you to the list of users notified when a new product is added',
    'unsubscribe'   : 'Removes you to the list of users notified when a new product is added'
}


@bot.message_handler(commands=['start'])
def greet(msg):
    bot.reply_to(msg, "beep boop... Hola Mundo! :3")
    subscribe(msg)
    bot.send_message(msg.chat.id, "No olvides consultar /help")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data:
        bot.send_message(call.from_user.id, "...Mostrando tus productos...")
        products(call.message, call.data)
    else:
        bot.answer_callback_query(call.id, "Invalid CallBack")

@bot.message_handler(commands=['help'])
def command_help(msg):
    help_text = "The following commands are available: \n\n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(msg.chat.id, help_text)  # send the generated help page

@bot.message_handler(commands=['ping'])
def greet(msg):
    bot.reply_to(msg, "beep boop... Pong! :3")

@bot.message_handler(commands=['categories'])
def categories(msg):
    response = requests.get(BASE_URL+ "/api/db/categories")
    categories = response.json()['data']
    bot.send_message(msg.chat.id, "Selecciona una Categoría...", reply_markup=gen_markup(categories))

@bot.message_handler(commands=['products'])
def products(msg, catego:str):
    response = requests.get(BASE_URL+ "/api/db/categories/"+ catego)
    products = response.json()['data']
    for product in products:
        text_content = product['name']+"\n\n   "+product['price']+"\n\n  "+product['url']
        bot.send_message(msg.chat.id, text_content)

@bot.message_handler(commands=['subscribe'])
def subscribe(msg):
    if not(msg.chat.id in subscribed):
        subscribed.append(msg.chat.id)
        bot.send_message(msg.chat.id, "Has sido subscrito, recibirás un mensaje cuando se agregue un producto nuevo")
    print(subscribed)

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(msg):
    if msg.chat.id in subscribed:
        subscribed.remove(msg.chat.id)
        bot.send_message(msg.chat.id, "Desubscrito, No recibiras mas mensajes")
    print(subscribed)


def schedule_msg(chats : list):
    response = requests.get(BASE_URL+ "/api/v1/new")
    products = response.json()['data']
    if products != []:
        for product in products:
            text_content = product['name']+"\n\n   "+product['price']+"\n\n  "+product['url']
            for chat in chats:
                bot.send_message(chat, text_content)

def gen_markup(categories):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for category in categories:
        markup.add(InlineKeyboardButton(category, callback_data=category))
    return markup

#schedule.every(10).seconds.do(schedule_msg, subscribed)


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)