import telebot
import telegram
import time
import pyairtable
import requests
import json
import pickle
from telebot import types
from telegram import ParseMode
#from telegram import MessageEntity
print('bot has started') 
#bot = telebot.TeleBot('5865283503:AAHI8sUoRRzDh3d0w1TpNnY35ymAqDTv5A4') #this is test
bot = telebot.TeleBot('5806434689:AAG383Pr1XxSpl4vjJ9rNFR27xJJA19bs0g') #this is prod
airtable_reg_name = '%E2%9C%85%20Registration'
airtable_event_name = '%F0%9F%8C%9F%20Event'
airtable_api_kay  = 'keyEEMaILmFa8kveA' #'keyItMsd5dUq2nC0P'
airtable_reg_base_ID = 'app7g2ANnagHYZkZ8'
airtable_event_base_ID = 'app7g2ANnagHYZkZ8'
airtable_view='%D0%9F%D1%80%D0%B5%D0%B4%D1%81%D1%82%D0%BE%D1%8F%D1%89%D0%B8%D0%B5%20%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D1%8F'
endpoint_reg='https://api.airtable.com/v0/{}/{}?&view={}'.format(airtable_reg_base_ID, airtable_reg_name, airtable_view)
endpoint_event='https://api.airtable.com/v0/{}/{}?&view=Future events'.format(airtable_event_base_ID, airtable_event_name)
headers = {
    "Authorization": "Bearer {}".format(airtable_api_kay),
    "Content-Type": "application/json"
    }

#do buttons

btn1 = types.KeyboardButton("Мои регистрации")
btn2 = types.KeyboardButton("Отправить напоминание")
btn3 = types.KeyboardButton("test")
backbtn = types.KeyboardButton("Назад")
adminlist=open('admin_list.txt', 'r', encoding='UTF-8').read().split('\n')

#create dicts that coteins users nicks and all them events
user_event_names_dict = {}                      #{nick: event_name, event_name}
event_name_event_id_dict = {}                   #{event_id: event_name <-/-> event_name: event_id}
user_names_chatid_dict = {}                     #{nick: chatid <-/-> chatid: nick}
with open('user_names_chatid.pkl', 'rb') as f:  #load DB of users
    user_names_chatid_dict=pickle.load(f)
event_names_chatid_dict ={}                     #{event_name: chatid, chatid}


def request_user_event_names():
    
    response_reg = requests.get(endpoint_reg, headers=headers)
    database_reg = response_reg.json()
    database_reg_len=len(database_reg['records'])
    response_event = requests.get(endpoint_event, headers=headers)
    database_event = response_event.json()
    database_event_len=len(database_event['records'])

    #create dict {event_id: event_name <-/->event_name:event_id}
    for i in range(database_event_len):
        event_id=database_event['records'][i]['id']
        event_name=database_event['records'][i]['fields']['Name event']
        event_name_event_id_dict[event_id]=event_name
        event_name_event_id_dict[event_name]=event_id
    
    #create dict {nick: event_name, event_name}
    for i in range(database_reg_len):
        nick=database_reg['records'][i]['fields']['You login in TG (reg)'].lower().replace(" ", "")
        event_id=''.join(database_reg['records'][i]['fields']['Event for reg'])
        try:
            event_name=event_name_event_id_dict[event_id].split('{;}')
            if nick[0]!='@':
                nick="@"+nick
            if nick not in user_event_names_dict:
                user_event_names_dict[nick]=event_name
            if ''.join(event_name) not in user_event_names_dict[nick]:
                user_event_names_dict[nick].append(event_name_event_id_dict[event_id])

            #create dict {event_name: chatid, chatid}
            if nick in user_names_chatid_dict:
                chatid=str(user_names_chatid_dict[nick]).split('{;}')
                if ''.join(event_name) not in event_names_chatid_dict:
                    event_names_chatid_dict[''.join(event_name)]=chatid
                elif ''.join(chatid) not in event_names_chatid_dict[''.join(event_name)]:
                    event_names_chatid_dict[''.join(event_name)].append(''.join(chatid))
        except:
            i+=1
    print('BD была обновлена')

request_user_event_names()

user_name={}
AdminAccess={}
eventList={}
eventIDList={}
user_list={}
pnick={}

@bot.message_handler(commands=["start"])
def Start(m):
    
    user_id = m.chat.id
    nick=m.from_user.username
    print(m.from_user.username,  ' нажал \start')

    #call markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btn1)
    if m.from_user.username in adminlist:
        print(m.from_user.username, 'взял(а) админский доступ')
        markup.add(btn2,btn3)
    
    #send helo text
    hello_text = open('./hello.txt', 'r', encoding='UTF-8').read()
    bot.send_message(m.from_user.id, text = "".join(hello_text), parse_mode=ParseMode.HTML, reply_markup=markup,disable_web_page_preview=True)

    add_user(m)
        
    @bot.message_handler(content_types=["text"])
    def handle_text(message):
        user_id = message.chat.id

        #registration check
        if message.text.strip() == 'Мои регистрации':
            try:
                request_user_event_names()
                user_id = message.chat.id
                pnick[user_id]='@'+message.from_user.username.lower()
                if pnick[user_id] in user_event_names_dict:
                    eventList[user_id]=user_event_names_dict[pnick[user_id]]
                    bot.send_message(user_id, text = "Вот мероприятия, на которые ты зарегистрирован(а):")
                    bot.send_message(user_id, text = "\n".join(eventList[user_id]))
                    eventList[user_id]=[]
                else:
                    bot.send_message(user_id, text = "Ого! Ты не зарегистрирован(а) ни на одно мероприятие(")
                
            except Exception as ex:
                bot.send_message(user_id, text = "Для того чтобы проверить свои регистрации, нужно иметь ник с @")
                main_menu(message)
            print(message.from_user.username,  ' запросил свои регистрции')
        #rassylka
        if message.text.strip() == 'Отправить напоминание' and message.from_user.username in adminlist:
            print(m.from_user.username, 'взял(а) админский доступ')
            user_id = message.chat.id
            eventList[user_id]=list(event_names_chatid_dict.keys())
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i  in range(len(eventList[user_id])):
                btn = types.KeyboardButton(eventList[user_id][i])
                markup.add(btn)
            markup.add(backbtn)
            send=bot.send_message(user_id, text = 'vot meropriyatia', reply_markup=markup)
            bot.register_next_step_handler(send, chose_event_for_spam)

        #if message.text.strip() == 'test':
            #main_menu(message)


def add_user(m):
    #add to dict if there is no {nick: chatid <-/-> chatid: nick}
    nick=m.from_user.username
    if nick==None:
        nick='@nobody'+str(m.chat.id)
    user_id=m.chat.id
    if nick[0]!='@':
        nick="@"+nick
    if nick not in user_names_chatid_dict or user_id not in user_names_chatid_dict:
        user_names_chatid_dict[nick.lower()]=user_id
        user_names_chatid_dict[user_id]=nick.lower()
        print(nick, 'добавился в юзерлист')
    with open('user_names_chatid.pkl', 'wb') as f:
            pickle.dump(user_names_chatid_dict, f, pickle.HIGHEST_PROTOCOL) #and save

def chose_event_for_spam(message):
    
    user_id = message.chat.id
    eventList[user_id]=list(event_names_chatid_dict.keys())
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    if message.text in eventList[user_id]:
        event_for_spam=message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        send=bot.send_message(user_id, text = 'pishi text', reply_markup=markup)
        bot.register_next_step_handler(send, ask_send_spam, event_for_spam)
    elif message.text=='Назад':
        main_menu(message)
    else:
        send=bot.send_message(user_id, text = 'net takogo', reply_markup=markup)
    
def ask_send_spam(message, event_for_spam):
    if message.text=='Назад':
        main_menu(message)
    else:
        user_id = message.chat.id
        message_for_spam=message
        list_of_spam_niks=[]
        list_of_spam=list(event_names_chatid_dict[event_for_spam])
        for i in range(len(list_of_spam)):
            list_of_spam_niks.append(user_names_chatid_dict[int(list_of_spam[i])])

        btn1=types.KeyboardButton('bahut rassilky')
        btn2=types.KeyboardButton('galya! otmena')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btn1, btn2)
        
        try:
            bot.send_message(user_id, text = 'otpravit soobsheie:')
            bot.send_message(user_id, message_for_spam.text)
            bot.send_message(user_id, text = 'vot etim rebyatam?')
            send=bot.send_message(user_id, text = ', '.join(list_of_spam_niks), reply_markup=markup)
            bot.register_next_step_handler(send, send_spam, message_for_spam, list_of_spam, list_of_spam_niks)
        except Exception as ex:
            bot.send_photo(user_id, photo=open('huinia.jpg', 'rb'))
            bot.register_next_step_handler(message_for_spam, ask_send_spam, event_for_spam)
def send_spam(message, message_for_spam, list_of_spam, list_of_spam_niks):
    user_id = message.chat.id
    if message.text=='bahut rassilky':
        for i in range(len(list_of_spam)):
            bot.send_message(list_of_spam[i], text=message_for_spam.text)
        bot.send_message(user_id, text = 'otpravil eto: ' + message_for_spam.text)
        bot.send_message(user_id, text = 'etim: '+', '.join(list_of_spam_niks))
        print(message.from_user.username,  ' дал рассылку')
        main_menu(message)
    elif message.text=='galya! otmena':
        main_menu(message)
    else:
        send=bot.send_message(user_id, text = 'eto ne otvet')
        bot.register_next_step_handler(send, send_spam, message_for_spam, list_of_spam, list_of_spam_niks)

def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btn1)
    if message.from_user.username in adminlist:
        AdminAccess[message.chat.id]=True
        markup.add(btn2,btn3)
    send=bot.send_message(message.chat.id, text = 'Главное меню', reply_markup=markup)




bot.polling(none_stop=True, interval=0)



























