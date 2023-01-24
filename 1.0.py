import telebot
import telegram
import time
import pyairtable
import requests
import json
from telebot import types
from telegram import ParseMode

bot = telebot.TeleBot('5806434689:AAG383Pr1XxSpl4vjJ9rNFR27xJJA19bs0g')
user_name={}
@bot.message_handler(commands=["start"])
def Start(m):
    
    airtable_reg_name = '%E2%9C%85%20Registration'
    airtable_event_name = '%F0%9F%8C%9F%20Event'
    airtable_api_kay  = 'keyItMsd5dUq2nC0P'
    airtable_reg_base_ID = 'app7g2ANnagHYZkZ8'
    airtable_event_base_ID = 'app7g2ANnagHYZkZ8'
    airtable_view='%D0%9F%D1%80%D0%B5%D0%B4%D1%81%D1%82%D0%BE%D1%8F%D1%89%D0%B8%D0%B5%20%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D1%8F'
    endpoint_reg='https://api.airtable.com/v0/{}/{}?&view={}'.format(airtable_reg_base_ID, airtable_reg_name, airtable_view)
    endpoint_event='https://api.airtable.com/v0/{}/{}'.format(airtable_event_base_ID, airtable_event_name)
    headers = {
        "Authorization": "Bearer {}".format(airtable_api_kay),
        "Content-Type": "application/json"
        }
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Мои регистрации")
    markup.add(btn1)
    hello_text = open('./hello.txt', 'r', encoding='UTF-8',).read()
    bot.send_message(m.from_user.id, text = "".join(hello_text), parse_mode=ParseMode.HTML, reply_markup=markup)
    @bot.message_handler(content_types=["text"])
    def handle_text(message):

        if message.text.strip() == 'Мои регистрации':
            user_id = message.chat.id
            user_name[user_id] = message.from_user.username
            response_reg = requests.get(endpoint_reg, headers=headers)
            database_reg = response_reg.json()
            database_reg_len=len(database_reg['records'])
            response_event = requests.get(endpoint_event, headers=headers)
            database_event = response_event.json()
            database_event_len=len(database_event['records'])
            evetList=[]
            for i in range(database_reg_len):
                try:
                    database_reg['records'][i]['fields']['You login in TG (reg)'].lower()==user_name[user_id].lower()
                except: 
                    i=i+1
                if database_reg['records'][i]['fields']['You login in TG (reg)'].lower()==user_name[user_id].lower() or database_reg['records'][i]['fields']['You login in TG (reg)'].lower()=='@{}'.format(user_name[user_id]).lower():
                    event_ID=''.join(database_reg['records'][i]['fields']['Event for reg'])
                    for j in range(database_event_len):
                        if database_event['records'][j]['id']==event_ID:
                            event_Name=database_event['records'][j]['fields']['Name event']
                            evetList.append(event_Name)
            if evetList==[]:
                bot.send_message(message.from_user.id, text = "Ого! Ты не зарегистрирован(а) ни на одно мероприятие(")
            else:
                evetList.insert(0, "Вот мероприятия, на которые ты зарегистрирован(а):")
                bot.send_message(message.from_user.id, text = "\n".join(evetList))
                evetList=[]
    
    
bot.polling(none_stop=True, interval=0)
























