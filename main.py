import telebot
import constants
import requests
import pickle
import os
#from flask import Flask, request
import logging

#-----------------
API_TOKEN = constants.token
appid = constants.appid
units = "metric"



bot = telebot.TeleBot(API_TOKEN)
bot.delete_webhook()
#server = Flask(__name__)

def deserialize(file_name):
    with open(file_name, 'rb') as f:
        return pickle.load(f)


def serialize(data, file_name):
    with open(file_name, 'wb') as f:
        pickle.dump(data, f)


#city = 'Kiev'
#serialize(city, 'data.pickle')


def log(message, answer):
    print("\n-----------")
    from datetime import datetime
    print((datetime.now()))
    print(("Message from {0} {1}. ( id = {2} ) \n text : {3}".format(message.from_user.first_name,
                                                                    message.from_user.last_name,
                                                                    str(message.from_user.id),
                                                                    message.text)))
    print(answer)


@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.chat.id, """Bot lets you to know weather with a simply commands.""")


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', '/stop')
    #user_markup.row('today', 'tomorrow', 'after tomorrow')
    bot.send_message(message.from_user.id, 'Welcome...\n Type some city to get weather (ex. "Kiev city")',
                     reply_markup=user_markup)


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, '..', reply_markup=hide_markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    buff = str(message.text)
    if 'city' in buff:
        words = buff.split()
        bot.send_message(message.from_user.id, 'Wait a bit...')
        req_city = ' '.join(c for c in words if c != 'city')
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/weather?",
                            params={'q': req_city, 'units': units, 'APPID': appid})
            data = res.json()
            data['weather'][0]['description']
        except Exception as e:
            bot.send_message(message.from_user.id, "I don't know this city, please type another one or fix existing...")
            req_city = deserialize('data.pickle')
            print(req_city)
            res = requests.get("http://api.openweathermap.org/data/2.5/weather?",
                            params={'q': req_city, 'units': units, 'APPID': appid})
            data = res.json()
            bot.send_message(message.from_user.id, "Here is the weather for the last correct city.")
        else:
            city = req_city
            serialize(city, 'data.pickle')
        finally:
            result = dict()
            print(data)
            result['description'] = data['weather'][0]['description']
            result['temperature'] = str(data['main']['temp'])+' C'
            result['min temperature'] = str(data['main']['temp_min'])+' C'
            result['max temperature'] = str(data['main']['temp_max'])+' C'
            result['wind'] = str(data['wind']['speed']) + 'm/s'
            result['name'] = data['name']

            bot.send_message(message.from_user.id,
"""Weather in {0} tomorrow : {1}
Temperature: {2}
Minimal temperature: {3}
Maximal temperature: {4}
Wind speed: {5}""".format(result['name'], result['description'],
                             result['temperature'], result['min temperature'],
                             result['max temperature'], result['wind']))

            log(message, '')

if __name__=='__main__':
    bot.polling(none_stop=True)

#@server.route("/")
#def webhook():
#    bot.remote_webhook()
#    bot.set_webhook(url="https://aqueous-sierra-16451.herokuapp.com/")
#    return "!", 200


#server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
