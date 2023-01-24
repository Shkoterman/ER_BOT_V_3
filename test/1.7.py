import datetime
import telebot
import requests
import pickle
import random
from datetime import *  
from airtable import *
from config_file_test import * #this is test
#from config_file_prod import * #this is prod
from telebot import types
from telegram import ParseMode
print('bot has started')
print(BD_Mode)

bot = telebot.TeleBot('5865283503:AAHI8sUoRRzDh3d0w1TpNnY35ymAqDTv5A4')  # this is test
#bot = telebot.TeleBot('5806434689:AAG383Pr1XxSpl4vjJ9rNFR27xJJA19bs0g') # this is prod

# do buttons
myregistrationbtn = types.KeyboardButton("Мои регистрации")
sendreminderbtn = types.KeyboardButton("Отправить напоминание")
testbtn = types.KeyboardButton("test")
regoneventbtn = types.KeyboardButton('Зарегистрироваться на мероприятие')
changenamebtn = types.KeyboardButton('Изменить имя')
changenickbtn = types.KeyboardButton('Изменить ник')
backbtn = types.KeyboardButton("Отмена")
yesbtn = types.KeyboardButton('Да')
nobtn = types.KeyboardButton('Нет')
changebtn = types.KeyboardButton('Изменить ник или имя')
feedbackbtn = types.KeyboardButton('Разослать запрос фидбэка')
allaoboutsubscriptionbtn = types.KeyboardButton('Все про подписку')
adminlist = open('admin_list.txt', 'r', encoding='UTF-8').read().split('\n') #открываю txt со списком админов
testq1=types.KeyboardButton('Посмотреть вариант 1')
testq2=types.KeyboardButton('Посмотреть вариант 2')
testq3=types.KeyboardButton('Посмотреть вариант 3')
test1=types.KeyboardButton('Отмена')
test2=types.KeyboardButton('Отмена (Главное меню)')
test3=types.KeyboardButton('Главное меню')


# create dicts that coteins users nicks and all them events
user_event_names_dict = {}                      # {nick: event_name, event_name}
event_name_event_id_dict = {}                   # {event_id: event_name <-/-> event_name: event_id}
user_names_chatid_dict = {}                     # {nick: chatid <-/-> chatid: nick}
with open('user_names_chatid.pkl', 'rb') as f:  # load DB of users
    user_names_chatid_dict = pickle.load(f)
event_names_chatid_dict = {}                    # {event_name: chatid, chatid}
eventList = {}                                  #словарь с персональными списками мероприятий
pnick = {}
is_user_subscribed={}

#этот метод собирает данные из эйртэйбла !!!его можно переделать и сделать быстрее и качественней и возможно проще используя библиотеку airtable и вще лчше разделить на пару методов
def request_user_event_names():
    user_event_names_dict.clear()                                           #так как дальше использую аппенд, тут очищаю словарь
    response_reg = requests.get(endpoint_reg, headers=headers_R)            #запрос в таблицу registration
    database_reg = response_reg.json()                                      #в джейсон его
    database_reg_len = len(database_reg['records'])                         #количество записей
    response_event = requests.get(endpoint_future_event, headers=headers_R) #запрос в таблицу Events
    database_event = response_event.json()                                  #в джейсон его
    database_event_len = len(database_event['records'])                     #количество записей

    # create dict {event_id: event_name <-/->event_name:event_id}
    for i in range(database_event_len):
        event_id = database_event['records'][i]['id']                       #эвент айди из эйртэйбла
        event_name = database_event['records'][i]['fields']['Name event']   #название эвента из эйртэйбла
        event_name_event_id_dict[event_id] = event_name.strip()             #записываю
        event_name_event_id_dict[event_name.strip()] = event_id             #зеркалю
    
    # c reate dict {nick: event_name, event_name}
    for i in range(database_reg_len):
        try:
            nick = database_reg['records'][i]['fields']['You login in TG (reg)'].lower().replace(" ", "")
            event_id = ''.join(database_reg['records'][i]['fields']['Event for reg'])
            event_name = event_name_event_id_dict[event_id].split('{;}')

            if nick[0] != '@':
                nick = "@"+nick
            if nick not in user_event_names_dict.keys():
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

request_user_event_names()

@bot.message_handler(commands=["start"])
def Start(m):
    print(m.from_user.username,  ' нажал \start')

    # call markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(testq1, testq2, testq3)
    if m.from_user.username in adminlist:
        print(m.from_user.username, 'взял(а) админский доступ')
        markup.add(sendreminderbtn, testbtn, feedbackbtn)
    
    # send helo text
    hello_text=open('./hello.txt', 'r', encoding='UTF-8').read()
    bot.send_message(m.from_user.id, text="Выбери вариант:", reply_markup=markup)

    #add_user(m)
        
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.chat.id

    # registration check
    if message.text.strip() == 'Посмотреть вариант 1':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(yesbtn, nobtn, test1)
        bot.send_message(user_id, text="Вариант 1", reply_markup=markup)
        bot.send_message(user_id, text="Что быпосмотреть другие варианты нажми любую кнопку")



    # rassylka
    elif message.text.strip() == 'Посмотреть вариант 2':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(yesbtn, nobtn, test2)
        bot.send_message(user_id, text="Вариант 2", reply_markup=markup)
        bot.send_message(user_id, text="Что быпосмотреть другие варианты нажми любую кнопку")

    # registration
    elif message.text.strip() == 'Посмотреть вариант 3':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(yesbtn, nobtn, test3)
        bot.send_message(user_id, text="Вариант 3", reply_markup=markup)
        bot.send_message(user_id, text="Что быпосмотреть другие варианты нажми любую кнопку")

    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(testq1, testq2, testq3)
        bot.send_message(message.chat.id, text='Угу', reply_markup=markup)

def add_user(m):
    # add to dict if there is no {nick: chatid <-/-> chatid: nick}
    nick = m.from_user.username.lower()
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
    request_user_event_names()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text in list(event_names_chatid_dict.keys()):
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

        myregistrationbtn = types.KeyboardButton('Разослать')
        sendreminderbtn = types.KeyboardButton('Галя, ОТМЕНА!!!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(myregistrationbtn, sendreminderbtn)
        
        try:
            bot.send_message(user_id, text='Отправить такое сообщение:')
            bot.send_message(user_id, message_for_spam.text)
            bot.send_message(user_id, text='Вот этим салатикам:')
            send=bot.send_message(user_id, text=', '.join(list_of_spam_niks), reply_markup=markup)
            bot.register_next_step_handler(send, send_spam, message_for_spam, list_of_spam, list_of_spam_niks)
        except Exception:
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
    markup.add(myregistrationbtn, regoneventbtn, allaoboutsubscriptionbtn)
    if message.from_user.username in adminlist:
        markup.add(sendreminderbtn, testbtn, feedbackbtn)
        types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.chat.id, text='Главное меню', reply_markup=markup)
    add_user(message)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def get_registration_list():
    response_avalible_event = requests.get(endpoint_avalible_event, headers=headers_R)
    database_avalible_event = response_avalible_event.json()
    database_avalible_event_len = len(database_avalible_event['records'])
    get_registration_list.avalible_event_name_event_id_dict_full = {}
    get_registration_list.avalible_event_name_event_id_dict_poor = {}
    for i in range(database_avalible_event_len):
        get_registration_list.avalible_event_name_event_id_dict_full[database_avalible_event['records'][i]['fields']['Name event'].strip()] = database_avalible_event['records'][i]['id']
        try:
           if database_avalible_event['records'][i]['fields']['is_it_subscribers_only']==True:
                i+=1
        except:
                get_registration_list.avalible_event_name_event_id_dict_poor[database_avalible_event['records'][i]['fields']['Name event'].strip()] = database_avalible_event['records'][i]['id']

def chose_event_for_reg(message, avalible_event_name_event_id_dict_full, avalible_event_name_event_id_dict_poor, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text in list(avalible_event_name_event_id_dict_full.keys()):
        reg_event_name = message.text.strip()
        reg_event_ID = avalible_event_name_event_id_dict_full[reg_event_name]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(nobtn, yesbtn, backbtn)
        send = bot.send_message(message.chat.id, text='Регистрирую @'+message.from_user.username+'?', reply_markup=markup)
        bot.register_next_step_handler(send, use_your_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(send, chose_event_for_reg, avalible_event_name_event_id_dict_full, avalible_event_name_event_id_dict_poor, reg_event_ID, reg_event_name, user_nick, user_name, markup)

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
            bot.send_message(message.chat.id, text='Введи имя:', reply_markup=markup)
            bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)
        elif alreadyregistred==False:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(nobtn, yesbtn, backbtn)
            bot.send_message(message.chat.id, text='Ты '+user_name+'?', reply_markup=markup)
            bot.register_next_step_handler(message, are_you, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Нет':
        types.ReplyKeyboardRemove()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        bot.send_message(message.chat.id, text='Введи ник:', reply_markup=markup)
        bot.register_next_step_handler(message, use_new_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
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
            bot.send_message(message.chat.id, text='Введи имя:', reply_markup=markup)
            bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)

    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, use_new_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def use_new_name (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Отмена':
        main_menu(message)
    elif message.text!=None:
        user_name=message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(changebtn, yesbtn, backbtn)
        bot.send_message(message.chat.id, text='Получается регистрирую так: \n Мероприятие: '+reg_event_name+' \n Ник: '+user_nick+' \n Имя: '+user_name, reply_markup=markup)
        bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
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
            send_for_reg(message, reg_event_ID, reg_event_name, user_nick, user_name)
    elif message.text == 'Изменить ник или имя':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(changenamebtn, changenickbtn, backbtn)
        bot.send_message(message.chat.id, text='Что изменить?', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def change_ik_or_username (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Изменить имя':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        what=0
        bot.send_message(message.chat.id, text='Введи новое имя', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username_get, reg_event_ID, reg_event_name, user_nick, user_name, what)
    elif message.text == 'Изменить ник':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        what=1
        bot.send_message(message.chat.id, text='Введи новый ник:', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username_get, reg_event_ID, reg_event_name, user_nick, user_name, what)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def change_ik_or_username_get (message, reg_event_ID, reg_event_name, user_nick, user_name, what):
        if message.text == 'Отмена':
            main_menu(message)
        elif what==0:
            user_name=message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(changebtn, yesbtn, backbtn)
            bot.send_message(message.chat.id,
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
            bot.send_message(message.chat.id,
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
    except Exception:
        try:
            find_it.user_name = airtable.search("You login in TG (reg)", user_nick_w_o)[0]['fields']['Как тебя зовут (имя и фамилия)']
        except Exception:
            try:
                find_it.user_name = airtable.search("You login in TG (reg)", user_nick)[0]['fields']['Как тебя зовут (имя и фамилия)']
            except Exception:
                find_it.user_name = None

def are_you (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Да':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(changebtn, yesbtn, backbtn)
        bot.send_message(message.chat.id, text='Получается регистрирую так:\nМероприятие: '+reg_event_name+'\nНик: '+user_nick+'\nИмя: '+user_name, reply_markup=markup)
        bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Нет':
        types.ReplyKeyboardRemove()
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)
        bot.send_message(message.chat.id, text='Введи имя:', reply_markup=markup)
        bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, are_you, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def send_for_reg(message, reg_event_ID, reg_event_name, user_nick, user_name):
    airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_RW)
    get_registration_list()
    try:
        user_id=user_names_chatid_dict[user_nick]
    except:
        user_id=966176056
    if bot.get_chat_member(-1001855787678, user_id).status!='left':  #966176056 message.chat.id
        registriruem = True
    elif reg_event_name in list(get_registration_list.avalible_event_name_event_id_dict_poor.keys()):
        registriruem = True
    else:
        bot.send_message(message.chat.id, text='Мероприятие, которое ты выбрал, сейчас доступно только для салатиков, которые подписались на клуб энсалады.\n \nЧтобы узнать подробней про варианты подписки и подписаться, нажимай на кнопку "Все про подписку"')
        registriruem = False
    #main_menu(message)

    if reg_event_name not in get_registration_list.avalible_event_name_event_id_dict_full.keys():
        bot.send_message(message.chat.id,
                     text='Вот блин! Во время регистрации кто-то подрезал последнее место на '+ reg_event_name+ '(((( Прости' )
    elif registriruem==True:
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
def chose_feedack_event(message):
    response_reg = requests.get(endpoint_past_event, headers=headers_R).json()['records']
    name_event=[]
    for i in range(len(response_reg)):
        eventday = datetime.strptime(response_reg[i]['fields']['Date'][:len(response_reg[i]['fields']['Date']) - 5],
                                     '%Y-%m-%dT%H:%M:%S')
        evenday = datetime(eventday.year, eventday.month, eventday.day).date()
        eventname = response_reg[i]['fields']['Name event']
        if evenday == date.today() - timedelta(days=1):
            name_event.append(eventname)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(name_event)):
        btn=types.KeyboardButton(name_event[i])
        markup.add(btn)
    markup.add(backbtn)
    bot.send_message(message.chat.id,
                     text='viberay', reply_markup=markup)
    bot.register_next_step_handler(message, give_feedback, name_event)

def give_feedback(message, name_event):
    if message.text in name_event:
        event_name=message.text
        airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_R)
        chat_ids=[]
        nicks=''
        dis_nicks = airtable.search("Event for reg", message.text)
        for i in range(len(dis_nicks)):
            try:
                nick=dis_nicks[i]['fields']['You login in TG (reg)'].lower()
                chat_ids.append(user_names_chatid_dict[nick])
                nicks += nick + ', '
            except:
                i+=1
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(yesbtn, backbtn)
        bot.send_message(message.chat.id, text='poluchat: '+nicks,reply_markup=markup)
        bot.register_next_step_handler(message, send_feedback, chat_ids, event_name)
    elif message.text=='Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
        bot.register_next_step_handler(message, give_feedback, name_event)

def send_feedback(message, chat_ids, event_name):
    if message.text=='Да':
        feedback_text = open('./feedback.txt', 'r', encoding='UTF-8').read()
        for i in range(len(chat_ids)):
            bot.send_message(chat_ids[i], text=feedback_text.replace("eventame", event_name, 1), parse_mode='Markdown', disable_web_page_preview=True)
        bot.send_message(message.chat.id, text='otpravil')
        main_menu(message)
    elif message.text=='Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
        bot.register_next_step_handler(message, send_feedback, chat_ids, event_name)

def error():
    try:
        bot.polling(none_stop=True, interval=0)

    except Exception as ex:
        print('ERROR: ', ex)
        error()
error()
    



























