import telebot
import telegram
import time
import pyairtable
import requests
import json
import pickle
#import airtable
import random

from airtable import *
#from config_file_test import *
from config_file_prod import *
from telebot import types
from telegram import ParseMode
from telegram import MessageEntity
print('bot has started')
print(BD_Mode)

#bot = telebot.TeleBot('5865283503:AAHI8sUoRRzDh3d0w1TpNnY35ymAqDTv5A4')  # this is test
bot = telebot.TeleBot('5806434689:AAG383Pr1XxSpl4vjJ9rNFR27xJJA19bs0g') # this is prod

# do buttons

btn1 = types.KeyboardButton("Мои регистрации")
btn2 = types.KeyboardButton("Отправить напоминание")
btn3 = types.KeyboardButton("test")
btn4 = types.KeyboardButton('Зарегистрироваться')
btn5 = types.KeyboardButton('Изменить имя')
btn6 = types.KeyboardButton('Изменить ник')
backbtn = types.KeyboardButton("Отмена")
yesbtn = types.KeyboardButton('Да')
nobtn = types.KeyboardButton('Нет')
changebtn = types.KeyboardButton('Изменить ник или имя')
adminlist = open('admin_list.txt', 'r', encoding='UTF-8').read().split('\n')


# create dicts that coteins users nicks and all them events
user_event_names_dict = {}                      # {nick: event_name, event_name}
event_name_event_id_dict = {}                   # {event_id: event_name <-/-> event_name: event_id}
user_names_chatid_dict = {}                     # {nick: chatid <-/-> chatid: nick}
with open('user_names_chatid.pkl', 'rb') as f:  # load DB of users
    user_names_chatid_dict = pickle.load(f)
event_names_chatid_dict = {}                     # {event_name: chatid, chatid}
#avalible_event_name_event_id_dict = {}
#user_names_user_names_dict = {}                 # {nick: name <-/-> name: nick}
api_key_R = 'keyItMsd5dUq2nC0P'
api_key_RW = 'keyEEMaILmFa8kveA'

def request_user_event_names():
    
    response_reg = requests.get(endpoint_reg, headers=headers_R)
    database_reg = response_reg.json()
    database_reg_len = len(database_reg['records'])
    response_event = requests.get(endpoint_future_event, headers=headers_R)
    database_event = response_event.json()
    database_event_len = len(database_event['records'])

    # create dict {event_id: event_name <-/->event_name:event_id}
    for i in range(database_event_len):
        event_id = database_event['records'][i]['id']
        event_name = database_event['records'][i]['fields']['Name event']
        event_name_event_id_dict[event_id] = event_name.strip()
        event_name_event_id_dict[event_name.strip()] = event_id
    
    # c reate dict {nick: event_name, event_name}
    for i in range(database_reg_len):
        try:
            nick = database_reg['records'][i]['fields']['You login in TG (reg)'].lower().replace(" ", "")
            event_id = ''.join(database_reg['records'][i]['fields']['Event for reg'])
            event_name = event_name_event_id_dict[event_id].split('{;}')

            if nick[0] != '@':
                nick = "@"+nick
            if nick not in user_event_names_dict:
                user_event_names_dict[nick] = event_name
            if ''.join(event_name) not in user_event_names_dict[nick]:
                user_event_names_dict[nick].append(event_name_event_id_dict[event_id])

            # create dict {event_name: chatid, chatid}
            if nick in user_names_chatid_dict:
                chatid = str(user_names_chatid_dict[nick]).split('{;}')
                if ''.join(event_name) not in event_names_chatid_dict:
                    event_names_chatid_dict[''.join(event_name)] = chatid
                elif ''.join(chatid) not in event_names_chatid_dict[''.join(event_name)]:
                    event_names_chatid_dict[''.join(event_name)].append(''.join(chatid))
        except:
            i += 1
    print('BD была обновлена')

request_user_event_names()

user_name = {}
AdminAccess = {}
eventList = {}
eventIDList = {}
user_list = {}
pnick = {}


@bot.message_handler(commands=["start"])
def Start(m):
    
    user_id = m.chat.id
    nick = m.from_user.username
    print(m.from_user.username,  ' нажал \start')

    # call markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btn1, btn4)
    if m.from_user.username in adminlist:
        print(m.from_user.username, 'взял(а) админский доступ')
        markup.add(btn2, btn3)
    
    # send helo text
    hello_text=open('./hello.txt', 'r', encoding='UTF-8').read()
    bot.send_message(m.from_user.id, text="".join(hello_text), parse_mode=ParseMode.HTML, reply_markup=markup,disable_web_page_preview=True)

    add_user(m)
        
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.chat.id

    # registration check
    if message.text.strip() == 'Мои регистрации':
        try:
            add_user(message)
            request_user_event_names()
            user_id = message.chat.id
            pnick[user_id] = '@'+message.from_user.username.lower()
            if pnick[user_id] in user_event_names_dict:
                eventList[user_id] = user_event_names_dict[pnick[user_id]]
                bot.send_message(user_id, text="Вот мероприятия, на которые ты зарегистрирован(а):")
                bot.send_message(user_id, text="\n".join(eventList[user_id]))
                eventList[user_id] = []
            else:
                bot.send_message(user_id, text="Ого! Ты не зарегистрирован(а) ни на одно мероприятие(")
                
        except Exception as ex:
            bot.send_message(user_id, text="Для того чтобы проверить свои регистрации, нужно иметь ник с @")
            main_menu(message)
        print(message.from_user.username,  ' запросил свои регистрции')

    # rassylka
    if message.text.strip() == 'Отправить напоминание' and message.from_user.username in adminlist:
        print(message.from_user.username, 'взял(а) админский доступ')
        user_id = message.chat.id
        eventList[user_id] = list(event_names_chatid_dict.keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(len(eventList[user_id])):
            btn = types.KeyboardButton(eventList[user_id][i])
            markup.add(btn)
        markup.add(backbtn)
        send=bot.send_message(user_id, text='Выбери мероприятие:', reply_markup=markup)
        bot.register_next_step_handler(send, chose_event_for_spam)

    # registration
    if message.text.strip() == 'Зарегистрироваться':
        get_registration_list()
        if message.from_user.username==None:
            bot.send_message(message.chat.id, text='Для того чтобы зарегистрироваться, нужно иметь ник с @')
            main_menu(message)

        elif get_registration_list.avalible_event_name_event_id_dict == {}:
            bot.send_message(message.chat.id, text='О, блин! Нет доступных меропиятий(((')
            main_menu(message)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in range(len(get_registration_list.avalible_event_name_event_id_dict)):
                btn = types.KeyboardButton(list(get_registration_list.avalible_event_name_event_id_dict.keys())[i])
                markup.add(btn)
            markup.add(backbtn)
            send=bot.send_message(message.chat.id, text='Выбери мероприятие:', reply_markup=markup)
            reg_event_ID = None
            reg_event_name = None
            user_nick = None
            user_name = None
            bot.register_next_step_handler(send, chose_event_for_reg, get_registration_list.avalible_event_name_event_id_dict, reg_event_ID, reg_event_name, user_nick, user_name, markup)
        
    # test
    if message.text.strip() == 'test':
        #user_nick=message.from_user.username
        #find_it(user_nick)

        api_key = 'keyItMsd5dUq2nC0P'
        #airtable = Airtable('appfwHMDb5pQTDHf2', 'tblVtBtNbUCtHeHD7', api_key)
        #print(airtable.search("You login in TG (reg)", '@shkoterman')[0]['fields']['Как тебя зовут (имя и фамилия)'])

        #with open('user_names_names.pkl', 'wb') as f:
            #user_names_user_names_dict={}
            #pickle.dump(user_names_user_names_dict, f, pickle.HIGHEST_PROTOCOL)


        #send_for_reg('recNShITpyP1LqdYp'.split(), 'Shkoterman', 'hui')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(nobtn, yesbtn)
        use_your_username(message, 'recNShITpyP1LqdYp', '🤔 Бот эвент 2', markup)
def add_user(m):
    # add to dict if there is no {nick: chatid <-/-> chatid: nick}
    nick = m.from_user.username
    if nick==None:
        nick = '@nobody'+str(m.chat.id)
    user_id = m.chat.id
    if nick[0]!='@':
        nick = "@"+nick
    if nick not in user_names_chatid_dict or user_id not in user_names_chatid_dict:
        user_names_chatid_dict[nick.lower()] = user_id
        user_names_chatid_dict[user_id]=nick.lower()
        print(nick, 'добавился в юзерлист')
    with open('user_names_chatid.pkl', 'wb') as f:
            pickle.dump(user_names_chatid_dict, f, pickle.HIGHEST_PROTOCOL)  # and save

def chose_event_for_spam(message):
    user_id = message.chat.id
    eventList[user_id] = list(event_names_chatid_dict.keys())
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    if message.text in eventList[user_id]:
        event_for_spam = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        send = bot.send_message(user_id, text='Напиши сообщение. Не делай абондед ссылок, картинок и проч.', reply_markup=markup)
        bot.register_next_step_handler(send, ask_send_spam, event_for_spam)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        send=bot.send_photo(user_id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(send, chose_event_for_spam)
        
def ask_send_spam(message, event_for_spam):
    if message.text == 'Отмена':
        main_menu(message)
    else:
        user_id = message.chat.id
        message_for_spam = message
        list_of_spam_niks  = []
        list_of_spam = list(event_names_chatid_dict[event_for_spam])
        for i in range(len(list_of_spam)):
            list_of_spam_niks.append(user_names_chatid_dict[int(list_of_spam[i])])

        btn1 = types.KeyboardButton('Разослать')
        btn2 = types.KeyboardButton('Галя, ОТМЕНА!!!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btn1, btn2)
        
        try:
            bot.send_message(user_id, text='Отправить такое сообщение:')
            bot.send_message(user_id, message_for_spam.text)
            bot.send_message(user_id, text='Вот этим салатикам:')
            send=bot.send_message(user_id, text=', '.join(list_of_spam_niks), reply_markup=markup)
            bot.register_next_step_handler(send, send_spam, message_for_spam, list_of_spam, list_of_spam_niks)
        except Exception as ex:
            bot.send_photo(user_id, photo=open('huinia.jpg', 'rb'))
            bot.register_next_step_handler(message_for_spam, ask_send_spam, event_for_spam)
def send_spam(message, message_for_spam, list_of_spam, list_of_spam_niks):
    user_id = message.chat.id
    if message.text ==  'Разослать':
        for i in range(len(list_of_spam)):
            bot.send_message(list_of_spam[i], text=message_for_spam.text)
        bot.send_message(user_id, text='Я отправил это сообщение:')
        bot.send_message(user_id, text=message_for_spam.text)
        bot.send_message(user_id, text='Этим салатикам: '+', '.join(list_of_spam_niks))
        print(message.from_user.username,  ' дал рассылку')
        main_menu(message)
    elif message.text == 'Галя, ОТМЕНА!!!':
        main_menu(message)
    else:
        send = bot.send_photo(user_id, photo=open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'))
        bot.register_next_step_handler(send, send_spam, message_for_spam, list_of_spam, list_of_spam_niks)

def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btn1, btn4)
    if message.from_user.username in adminlist:
        AdminAccess[message.chat.id]=True
        markup.add(btn2, btn3)
    #bot.edit_message_reply_markup(chat_id=message.chat.id, reply_markup=markup)

    send=bot.send_message(message.chat.id, text='Главное меню', reply_markup=markup)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def get_registration_list():
    response_avalible_event = requests.get(endpoint_avalible_event, headers=headers_R)
    database_avalible_event = response_avalible_event.json()
    database_avalible_event_len = len(database_avalible_event['records'])
    get_registration_list.avalible_event_name_event_id_dict={}
    for i in range(database_avalible_event_len):
        get_registration_list.avalible_event_name_event_id_dict[database_avalible_event['records'][i]['fields']['Name event'].strip()] = database_avalible_event['records'][i]['id']
    # print(avalible_event_name_event_id_dict)  

def chose_event_for_reg(message, avalible_event_name_event_id_dict, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    #print(list(avalible_event_name_event_id_dict.keys()))
    if message.text in list(avalible_event_name_event_id_dict.keys()):
        reg_event_name = message.text.strip()
        reg_event_ID = avalible_event_name_event_id_dict[reg_event_name]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(nobtn, yesbtn, backbtn)
        send = bot.send_message(message.chat.id, text='Регистрирую @'+message.from_user.username+'? Если хочешь зарегистрировать другого человека, нажми "Нет", ', reply_markup=markup)
        bot.register_next_step_handler(send, use_your_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(send, chose_event_for_reg, avalible_event_name_event_id_dict, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def use_your_username (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Да':
        user_nick = '@'+message.from_user.username.lower()
        request_user_event_names()
        alreadyregistred=False
        if user_nick in user_event_names_dict.keys():
            if reg_event_name in user_event_names_dict[user_nick]:
                bot.send_message(message.chat.id, text=user_nick + ' уже зарегистрирован на мероприятие '+reg_event_name)
                main_menu(message)
                alreadyregistred=True
        find_it(user_nick)
        user_name = find_it.user_name
        if user_name is None and alreadyregistred==False:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(backbtn)
            send=bot.send_message(message.chat.id, text='Введи имя:', reply_markup=markup)
            bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)
        elif alreadyregistred==False:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(nobtn, yesbtn, backbtn)
            send=bot.send_message(message.chat.id, text='Ты '+user_name+'?', reply_markup=markup)
            bot.register_next_step_handler(message, are_you, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Нет':
        types.ReplyKeyboardRemove()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        send=bot.send_message(message.chat.id, text='Введи ник:', reply_markup=markup)
        bot.register_next_step_handler(message, use_new_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, use_your_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
        
def use_new_username (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Отмена':
        main_menu(message)
    elif user_name!=None:
        registration_on_event_chek(message, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text != None:
        user_nick = message.text
        if user_nick[0] != '@':
            user_nick = '@' + user_nick
        request_user_event_names()
        if user_nick in user_event_names_dict.keys():
            if reg_event_name in user_event_names_dict[user_nick]:
                bot.send_message(message.chat.id, text=user_nick + ' уже зарегистрирован на мероприятие ' + reg_event_name)
                main_menu(message)
        else:
            send = bot.send_message(message.chat.id, text='Введи имя:', reply_markup=markup)
            bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)

    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, use_new_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def use_new_name (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Отмена':
        main_menu(message)
    #elif user_name!=None:
        #print('1')

        #registration_on_event_chek(message, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text!=None:
        user_name=message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(changebtn, yesbtn, backbtn)
        send=bot.send_message(message.chat.id, text='Получается регистрирую так: \n Мероприятие: '+reg_event_name+' \n Ник: '+user_nick+' \n Имя: '+user_name, reply_markup=markup)
        bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def registration_on_event_chek(message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Да':
        with open('user_names_names.pkl', 'rb') as f1:
            user_names_user_names_dict = pickle.load(f1)
            user_nick_for_dict = user_nick.lower().strip()
            user_names_user_names_dict[user_nick_for_dict]=user_name
            user_names_user_names_dict[user_name]=user_nick_for_dict
            with open('user_names_names.pkl', 'wb') as f:
                pickle.dump(user_names_user_names_dict, f, pickle.HIGHEST_PROTOCOL)
            send_for_reg(message, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Изменить ник или имя':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btn5, btn6, backbtn)
        send = bot.send_message(message.chat.id, text='Что изменить?', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def change_ik_or_username (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Изменить имя':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        what=0
        send = bot.send_message(message.chat.id, text='Введи новое имя', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username_get, reg_event_ID, reg_event_name, user_nick, user_name, what, markup)
    elif message.text == 'Изменить ник':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        what=1
        send = bot.send_message(message.chat.id, text='Введи новый ник:', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username_get, reg_event_ID, reg_event_name, user_nick, user_name, what, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        send = bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def change_ik_or_username_get (message, reg_event_ID, reg_event_name, user_nick, user_name, what, markup):
        if message.text == 'Отмена':
            main_menu(message)
        elif what==0:
            user_name=message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(changebtn, yesbtn, backbtn)
            send = bot.send_message(message.chat.id,
                                    text='Получается регистрирую так: \n Мероприятие: ' + reg_event_name + ' \n Ник: ' + user_nick + ' \n Имя: ' + user_name,
                                    reply_markup=markup)
            bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick,
                                           user_name, markup)
        elif what==1:
            new_user_nick=message.text
            if new_user_nick[0] != '@':
                new_user_nick = '@' + new_user_nick
            old_user_nick=user_nick
            if old_user_nick[0] != '@':
                old_user_nick = '@' + old_user_nick
            request_user_event_names()
            if new_user_nick in user_event_names_dict.keys():
                if reg_event_name in user_event_names_dict[new_user_nick]:
                    bot.send_message(message.chat.id,
                                     text=new_user_nick + ' уже зарегистрирован на мероприятие ' + reg_event_name)
                    user_nick=old_user_nick
                else:
                    user_nick=new_user_nick
            else:
                user_nick = new_user_nick
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(changebtn, yesbtn, backbtn)
            send = bot.send_message(message.chat.id,
                                    text='Получается регистрирую так: \n Мероприятие: ' + reg_event_name + ' \n Ник: ' + user_nick + ' \n Имя: ' + user_name,
                                    reply_markup=markup)
            bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick,
                                           user_name, markup)

def find_it(user_nick):
    airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_R)
    if user_nick[0] == '@':
        user_nick_w_o = user_nick[1:]
    else:
        user_nick_w_o = user_nick
        user_nick = '@'+user_nick
    try:
        with open('user_names_names.pkl', 'rb') as f1:
            user_names_user_names_dict=pickle.load(f1)
            find_it.user_name = user_names_user_names_dict[user_nick.lower()]
    except Exception as ex:
        try:
            find_it.user_name = airtable.search("You login in TG (reg)", user_nick_w_o)[0]['fields']['Как тебя зовут (имя и фамилия)']
        except Exception as ex:
            try:
                find_it.user_name = airtable.search("You login in TG (reg)", user_nick)[0]['fields']['Как тебя зовут (имя и фамилия)']
            except Exception as ex:
                find_it.user_name = None

def are_you (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Да':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(changebtn, yesbtn, backbtn)
        send=bot.send_message(message.chat.id, text='Получается регистрирую так:\nМероприятие: '+reg_event_name+'\nНик: '+user_nick+'\nИмя: '+user_name, reply_markup=markup)
        bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Нет':
        types.ReplyKeyboardRemove()
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        send=bot.send_message(message.chat.id, text='Введи имя:', reply_markup=markup)
        bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, are_you, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def send_for_reg(message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_RW)
    get_registration_list()
    if reg_event_name not in get_registration_list.avalible_event_name_event_id_dict.keys():
        bot.send_message(message.chat.id,
                     text='Вот блин! Во время регистрации кто-то подрезал последнее место на '+ reg_event_name+ '(((( Прости' )
    else:
        airtable.insert(
            {you_login_in_TG_field: user_nick, event_for_reg_field: reg_event_ID.split(), whats_your_name_field: user_name})
        request_user_event_names()
        if user_nick[0]!='@':
            user_nick='@'+user_nick
        if reg_event_name in user_event_names_dict[user_nick]:
            bot.send_message(message.chat.id,
                             text=user_nick+' зарегистрирован на ' + reg_event_name)
        print('Регаю мероприятие: ' + reg_event_name + ' event ID: ' + str(
            reg_event_ID) + 'Ник: ' + user_nick + 'Имя: ' + user_name)
    main_menu(message)
def error():
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as ex:
        print('ERROR: ', ex)
        error()
error()
    
    


























