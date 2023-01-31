import datetime
import telebot
import requests
import pickle
import random
from datetime import *  
from airtable import *
#from config_file_test import * #this is test
from config_file_prod import * #this is prod
from telebot import types
from telegram import ParseMode

inlogtxt = datetime.now().strftime("%d-%m-%Y %H:%M") + ': bot has been started ' + '(' + BD_Mode + ')\n' #дописываю время
print(inlogtxt)                                                         #дублирую в консоль
with open('log.txt', 'r+', encoding='utf-16') as f:                     #открываю лог
    f.seek(0, 2)                                                        #перемещение курсора в конец файла
    f.write(inlogtxt)                                                   #собственно, запись

#bot = telebot.TeleBot('5865283503:AAHI8sUoRRzDh3d0w1TpNnY35ymAqDTv5A4')  # this is test
bot = telebot.TeleBot('5806434689:AAG383Pr1XxSpl4vjJ9rNFR27xJJA19bs0g') # this is prod

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
        #print(database_event['records'][i]['fields'])
        event_name = database_event['records'][i]['fields']['Name event']   #название эвента из эйртэйбла
        event_name_event_id_dict[event_id] = event_name.strip()             #записываю
        event_name_event_id_dict[event_name.strip()] = event_id             #зеркалю
    
    # c reate dict {nick: event_name, event_name}
    for i in range(database_reg_len):
        try:
            nick = database_reg['records'][i]['fields']['You login in TG (reg)'].lower().replace(" ", "")   #беру из ответа эйртэйбла тг ник
            event_id = ''.join(database_reg['records'][i]['fields']['Event for reg'])                       #и айди эвента
            event_name = event_name_event_id_dict[event_id].split('{;}')                                    #из словаря беру имя эвента по айди. по умолчанию возвращает элемент листа .сплит делает его стрингом

            if nick[0] != '@':                                                                              #привожу тг ник к виду: @xxxxx тоесть начинается на собаку без пробелов и все буквы маленькие
                nick = "@"+nick
            if nick not in user_event_names_dict.keys():                                                    #если тг ника нет в словаре, добавляю ключ и имя эвента
                user_event_names_dict[nick] = event_name
            if ''.join(event_name) not in user_event_names_dict[nick]:                                      #если есть, то только имя эвента
                user_event_names_dict[nick].append(event_name_event_id_dict[event_id])                      

            # create dict {event_name: chatid, chatid}
            if nick in user_names_chatid_dict:                                                              #в этом же цикле добавляю чатайди к имени эвента, это нужно для рассылки
                chatid = str(user_names_chatid_dict[nick]).split('{;}')                                     #о5 использую ебаный сплит, потомучтотупойсук
                if ''.join(event_name) not in event_names_chatid_dict:                                      #если имя эвента нет в словаре, добавляю ключ и чатайди
                    event_names_chatid_dict[''.join(event_name)] = chatid
                elif ''.join(chatid) not in event_names_chatid_dict[''.join(event_name)]:                   #если есть то добавляю чатайди
                    event_names_chatid_dict[''.join(event_name)].append(''.join(chatid))
        except:
            i += 1

request_user_event_names()                                                  #вызываю обновление БД

@bot.message_handler(commands=["start"])                                    #я не знаю что это(((( видимо штука которая ждёт сообщения, я хз
def Start(m):                                                               #первая встреча с дорогим пользователем
    write_in_log_regular_events(inlogtxt='@' + m.from_user.username + ' нажал_a \start')     #писька в лог

    # call markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)                #маркап это типа список кнопок. объявляю
    markup.add(myregistrationbtn, regoneventbtn, allaoboutsubscriptionbtn)  #добавляю
    if m.from_user.username in adminlist:                                   #если чел в админ листе добавляю админские кнопки
        markup.add(sendreminderbtn, testbtn, feedbackbtn)
        write_in_log_regular_events(inlogtxt='@' + m.from_user.username + ' взял_а админский доступ')                                              #писька в лог

    # send helo text
    hello_text=open('./hello_txt', 'r', encoding='UTF-8').read()
    bot.send_message(m.from_user.id, text="".join(hello_text), parse_mode=ParseMode.HTML, reply_markup=markup, disable_web_page_preview=True)

    add_user(m)                                                             #добавляю юзера в свой список если его там нет
        
@bot.message_handler(content_types=["text"])                                #я не знаю что это(((( видимо штука которая ждёт сообщения, я хз
def handle_text(message):
    user_id = message.chat.id                                               #это айди юзера. бот общается с пользователем только по айди

    # registration check
    if message.text.strip() == 'Мои регистрации':                           #тут и дальше тект сообщения интерпритируется как команда
        try:
            add_user(message)
            request_user_event_names()                                      #обновляю бд
            user_id = message.chat.id
            pnick[user_id] = '@'+message.from_user.username.lower()         #вместо переменной использую словарь, чтобы тг ники не перепутались когда два чела проверяют регу отдновременно

            if pnick[user_id] in user_event_names_dict:                                                 #проверка есть ли тг ник в словаре
                eventList[user_id] = user_event_names_dict[pnick[user_id]]                              #заполняю персональный лист мероприятий одним "словом" из словаря
                bot.send_message(user_id, text="Вот мероприятия, на которые ты зарегистрирован_а:")
                bot.send_message(user_id, text="\n".join(eventList[user_id]))
                eventList[user_id] = []                                                                 #очищаю для будующего использования
            else:
                bot.send_message(user_id, text="Ого! Ты не зарегистрирован_а ни на одно мероприятие(")
            main_menu(message)
        except Exception:
            bot.send_message(user_id, text="Для того чтобы проверить свои регистрации, нужно иметь ник с @")
            main_menu(message)
        write_in_log_regular_events(inlogtxt='@'+message.from_user.username +' запросил_a свои регистрции')              #писька в лог

    # registration
    elif message.text.strip() == 'Зарегистрироваться на мероприятие':
        get_registration_list()                                                                                         #получаю список мероприятий
        if message.from_user.username==None:                                                                            #если нет ника отвержение
            bot.send_message(message.chat.id, text='Для того чтобы зарегистрироваться, нужно иметь ник с @')
            main_menu(message)

        elif get_registration_list.avalible_event_name_event_id_dict_full == {}:                                        #на случай отсутствия мероприятий
            bot.send_message(message.chat.id, text='О, блин! Нет доступных меропиятий(((')
            main_menu(message)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in range(len(get_registration_list.avalible_event_name_event_id_dict_full)):                          #даю полный список мероприятий пользователю
                btn = types.KeyboardButton(list(get_registration_list.avalible_event_name_event_id_dict_full.keys())[i])
                markup.add(btn)
            markup.add(backbtn)                                                                                         #добавляю кнопку отмена
            send=bot.send_message(message.chat.id, text='Выбери мероприятие:', reply_markup=markup)
            reg_event_ID = None                                                                                         #даю пустые переменные, чтобы передать их дальше
            reg_event_name = None
            user_nick = None
            user_name = None
            bot.register_next_step_handler(send, chose_event_for_reg, get_registration_list.avalible_event_name_event_id_dict_full, get_registration_list.avalible_event_name_event_id_dict_poor, reg_event_ID, reg_event_name, user_nick, user_name, markup) #жду ответа от юзера и отсылаю ответ в

    elif message.text.strip() == 'Все про подписку':
        aboutsubtext = open('./allaoboutsubscription.txt', 'r', encoding='UTF-8').read()              #открываю текст из файла и отправляю
        bot.send_message(message.from_user.id, text="".join(aboutsubtext), parse_mode='Markdown',
                         disable_web_page_preview=True)
        write_in_log_regular_events(inlogtxt='@' + message.from_user.username + ' узнал все про подписку')

    elif message.text.strip() == 'Разослать запрос фидбэка' and message.from_user.username in adminlist:
        chose_feedack_event(message)                                                                                    #сразу в метод

    # rassylka
    elif message.text.strip() == 'Отправить напоминание' and message.from_user.username in adminlist:
        request_user_event_names()                                                                  #обновил базу
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(len(list(event_names_chatid_dict.keys()))):                                  #сделал все кнопки с названиями мероприятия
            btn = types.KeyboardButton(list(event_names_chatid_dict.keys())[i])
            markup.add(btn)
        markup.add(backbtn)                                                                         #добавка кнопки назад
        send=bot.send_message(message.chat.id, text='Выбери мероприятие:', reply_markup=markup)
        bot.register_next_step_handler(send, chose_event_for_spam)                                  #жду ответа от юзера и отсылаю ответ в chose_event_for_spam

    elif message.text.strip() == 'test':                                               #тестовая кнопка, без комментариев
        print('q')
        #feedback_text = open('./feedback.txt', 'r', encoding='UTF-8').read()
        #bot.send_message(message.chat.id, text=feedback_text.replace("eventame", 'eventname', 1), parse_mode='Markdown',
        #                 disable_web_page_preview=True)
        #airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_R)
        1==1
        #asd=asd+123
        #asd.append('reczEuuUW92Xt140D')
        #print(asd)
        ##dis_nicks = airtable.search('Event for reg', "💆‍♀️ GRL PWR BRUNCH - NY edition (15.12)")
        #dis_nicks = airtable.search('Date (from Event for reg)', '2023-01-06T17:02:00.000Z')
        #print(dis_nicks)

            #user_names_user_names_dict={}
            #user_names_user_names_dict['user_nick']='user_name'
            #user_names_user_names_dict['user_name']='user_nick'
            #with open('user_names_chatid.pkl', 'wb') as f:
                #pickle.dump(user_names_user_names_dict, f, pickle.HIGHEST_PROTOCOL)

    else:   #когда непонял команду
        bot.send_message(message.chat.id, text='К сожалению, меня пока не научили читать😔 Если вы хотите дать обратную связь или поделиться своими мыслями - пишите @julia_sergina. Если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        try:
            nick=message.from_user.username
            if nick == None:
                nick = 'nobody'
            write_in_log_misunderstand(inlogtxt='бот не понял команды от @' + nick + ': ' + message.text)
            write_feedback_at_airtale(message)
        except Exception as ex:
            write_in_log_error(inlogtxt=str(ex))
        main_menu(message)

def write_in_log_regular_events(inlogtxt):                                                 #запись текста в лог
    try:
        inlogtxt = datetime.now().strftime("%d-%m-%Y %H:%M") + ': ' + inlogtxt + '\n' #дописываю время
        print(inlogtxt)                                                         #дублирую в консоль
        with open('log.txt', 'r+', encoding='utf-16') as f:                     #открываю лог
            f.seek(0, 2)                                                        #перемещение курсора в конец файла
            f.write(inlogtxt)                                                   #собственно, запись
    except Exception as ex:
        write_in_log_error(str(ex))

def write_in_log_error(inlogtxt):                                                 #запись текста в лог
    inlogtxt = datetime.now().strftime("%d-%m-%Y %H:%M") + ': ERROR: ' + inlogtxt + '\n' #дописываю время
    print(inlogtxt)                                                         #дублирую в консоль
    with open('log_error.txt', 'r+', encoding='utf-16') as f:                     #открываю лог
        f.seek(0, 2)                                                        #перемещение курсора в конец файла
        f.write(inlogtxt)                                                   #собственно, запись

def write_in_log_misunderstand(inlogtxt):                                                 #запись текста в лог
    try:
        inlogtxt = datetime.now().strftime("%d-%m-%Y %H:%M") + ': ' + inlogtxt + '\n' #дописываю время
        print(inlogtxt)                                                         #дублирую в консоль
        with open('log_misunderstand.txt', 'r+', encoding='utf-16') as f:                     #открываю лог
            f.seek(0, 2)                                                        #перемещение курсора в конец файла
            f.write(inlogtxt)                                                   #собственно, запись
    except Exception as ex:
        write_in_log_error(str(ex))

def add_user(m):                                                            # add to dict if there is no {nick: chatid <-/-> chatid: nick}
    #nick = m.from_user.username.lower()                                     #делаю всё строчными
    if m.from_user.username==None:                                                          #если ника нет или скрыт, делаю искусственный ник
        nick = '@nobody'+str(m.chat.id)
    else:
        nick = '@' + m.from_user.username.lower()                               # добавляю @
    user_id = m.chat.id
    if nick not in user_names_chatid_dict or user_id not in user_names_chatid_dict: #если в локальной бд нет ника или айди добавляю
        user_names_chatid_dict[nick.lower()] = user_id
        user_names_chatid_dict[user_id]=nick.lower()
        write_in_log_regular_events(inlogtxt=nick + ' добавился в юзерлист')
    with open('user_names_chatid.pkl', 'wb') as f:
            pickle.dump(user_names_chatid_dict, f, pickle.HIGHEST_PROTOCOL)  #сохраняю в файл

def main_menu(message):                                                     #возвращает в главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(myregistrationbtn, regoneventbtn, allaoboutsubscriptionbtn)
    if message.from_user.username in adminlist:
        markup.add(sendreminderbtn, testbtn, feedbackbtn)
        types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(message.chat.id, text='Главное меню', reply_markup=markup)
    add_user(message)

def get_registration_list():        #метод возвращает два словаря. Со всеми эвентами и с беслпатными
    response_avalible_event = requests.get(endpoint_avalible_event, headers=headers_R)  #запрос в эиртэйбл
    database_avalible_event = response_avalible_event.json()
    database_avalible_event_len = len(database_avalible_event['records'])               #количество записей в нём
    get_registration_list.avalible_event_name_event_id_dict_full = {}                   #полный список мероприятий
    get_registration_list.avalible_event_name_event_id_dict_poor = {}                   #список бесплатных мероприятий
    for i in range(database_avalible_event_len):
        get_registration_list.avalible_event_name_event_id_dict_full[database_avalible_event['records'][i]['fields']['Name event'].strip()] = database_avalible_event['records'][i]['id']   #в любом случае записываю мероприятие в полный список
        try:        #я хз почему, но если в эйртэйбле не стоит галочка в поле, то в ответе ваще нет этого поля а если галочка стоит, то возвращает тру
           if database_avalible_event['records'][i]['fields']['is_it_subscribers_only']==True:  #если оно закрытое то не записываю его в спсиок открытых
                i+=1
        except:
                get_registration_list.avalible_event_name_event_id_dict_poor[database_avalible_event['records'][i]['fields']['Name event'].strip()] = database_avalible_event['records'][i]['id'] #еси в поле получилась ошибка значит по сути фэлс и это открытое мероприяте

def chose_event_for_spam(message):                                      #метод для написания текста рассыли
    request_user_event_names()                                          #обновляю бд
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text in list(event_names_chatid_dict.keys()):            #если юзер выбрал мероприятие
        event_for_spam = message.text                                   #название мероприятия это текст его сообщения
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(backbtn)                                             #кнопка отмены
        send = bot.send_message(message.chat.id, text='Напиши сообщение. Не делай абондед ссылок, картинок и проч.', reply_markup=markup)
        bot.register_next_step_handler(send, ask_send_spam, event_for_spam)     #жду сообщения от юзера и передаю его в ask_send_spam
    elif message.text == 'Отмена':
        main_menu(message)
    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')   #если юзер написал хоень, то смешная картинка
        bot.register_next_step_handler(send, chose_event_for_spam)                                                                  #и возвращаюсь в этот же метод
        
def ask_send_spam(message, event_for_spam):                             #последний шанс отменить всё
    if message.text == 'Отмена':
        main_menu(message)
    else:
        user_id = message.chat.id                                       #если текст не отмена, то это текст рассылки
        message_for_spam = message
        list_of_spam_niks  = []                                         #список ников (пока пустой) для рассылки
        list_of_spam = list(event_names_chatid_dict[event_for_spam])    #список айдишников для рассылки
        for i in range(len(list_of_spam)):
            list_of_spam_niks.append(user_names_chatid_dict[int(list_of_spam[i])])  #делаю список ников для рассылки
        myregistrationbtn = types.KeyboardButton('Разослать')           #пара кнопок
        sendreminderbtn = types.KeyboardButton('Галя, ОТМЕНА!!!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(myregistrationbtn, sendreminderbtn)
        try:                                                                #на случай если юзер не соблюл условия сообщения для рассылки
            bot.send_message(user_id, text='Отправить такое сообщение:')
            bot.send_message(user_id, message_for_spam.text)
            bot.send_message(user_id, text='Вот этим салатикам:')
            send=bot.send_message(user_id, text=', '.join(list_of_spam_niks), reply_markup=markup)
            bot.register_next_step_handler(send, send_spam, message_for_spam, list_of_spam, list_of_spam_niks) #жду подтерждения и отсылаю в след. метод
        except Exception:
            bot.send_photo(user_id, photo=open('huinia.jpg', 'rb'))         #на случай наёба с условиями - смешная картинка
            bot.register_next_step_handler(message_for_spam, ask_send_spam, event_for_spam) #и в предыдущий метод

def send_spam(message, message_for_spam, list_of_spam, list_of_spam_niks):  #сопсно рассылка
    user_id = message.chat.id
    if message.text ==  'Разослать':
        for i in range(len(list_of_spam)):                                  #каждому челу из словаря бахаю сообщение
            bot.send_message(list_of_spam[i], text=message_for_spam.text)
        bot.send_message(user_id, text='Я отправил это сообщение:')         #отчитываюсь отправителю
        bot.send_message(user_id, text=message_for_spam.text)
        bot.send_message(user_id, text='Этим салатикам: '+', '.join(list_of_spam_niks))
        write_in_log_regular_events(inlogtxt=message.from_user.username + ' дал рассылку')
        main_menu(message)
    elif message.text == 'Галя, ОТМЕНА!!!':
        main_menu(message)
    else:
        send = bot.send_photo(user_id, photo=open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'))
        bot.register_next_step_handler(send, send_spam, message_for_spam, list_of_spam, list_of_spam_niks) #если не отмена и не разослать, то возвращаюсь в предыдущий метод

# # # # # # # # # # # # # # # # # # # # # # # # # # # # тут огромный блок регистрации

def chose_event_for_reg(message, avalible_event_name_event_id_dict_full, avalible_event_name_event_id_dict_poor, reg_event_ID, reg_event_name, user_nick, user_name, markup):

    if bot.get_chat_member(-1001855787678, message.chat.id).status!='left':  #966176056
        registriruem = True
    elif message.text in list(avalible_event_name_event_id_dict_poor.keys()):
        registriruem = True
    else:
        bot.send_message(message.chat.id, text='Мероприятие, которое ты выбрал, сейчас доступно только для салатиков, которые подписались на клуб энсалады.\n \nЧтобы узнать подробней про варианты подписки и подписаться, нажимай на кнопку "Все про подписку"')
        registriruem = False

    if message.text in list(avalible_event_name_event_id_dict_full.keys()) and registriruem==True:
        reg_event_name = message.text.strip()
        reg_event_ID = avalible_event_name_event_id_dict_full[reg_event_name]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(nobtn, yesbtn, backbtn)
        send = bot.send_message(message.chat.id, text='Регистрирую @'+message.from_user.username+'?', reply_markup=markup)
        bot.register_next_step_handler(send, use_your_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Отмена' or registriruem==False:
        main_menu(message)
    else:
        send=bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        bot.register_next_step_handler(send, chose_event_for_reg, avalible_event_name_event_id_dict_full, avalible_event_name_event_id_dict_poor, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def use_your_username (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Да':
        user_nick = '@'+message.from_user.username.lower()
        request_user_event_names()
        alreadyregistred=False
        if user_nick in user_event_names_dict.keys():
            if reg_event_name in user_event_names_dict[user_nick]:
                bot.send_message(message.chat.id, text=user_nick + ' уже зарегистрирован_а на мероприятие '+reg_event_name)
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
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
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
                bot.send_message(message.chat.id, text=user_nick + ' уже зарегистрирован_а на мероприятие ' + reg_event_name)
                main_menu(message)
        else:
            bot.send_message(message.chat.id, text='Введи имя:', reply_markup=markup)
            bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)

    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        bot.register_next_step_handler(message, use_new_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def use_new_name (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Отмена':
        main_menu(message)
    elif message.text!=None:
        user_name=message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(changebtn, yesbtn, backbtn)
        bot.send_message(message.chat.id, text='Получается, регистрирую так? \n Мероприятие: '+reg_event_name+' \n Ник: '+user_nick+' \n Имя: '+user_name, reply_markup=markup)
        bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
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
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
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
                                    text='Получается, регистрирую так? \n Мероприятие: ' + reg_event_name + ' \n Ник: ' + user_nick + ' \n Имя: ' + user_name,
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
                                     text=new_user_nick + ' уже зарегистрирован_а на мероприятие ' + reg_event_name)
                    user_nick=old_user_nick
                else:
                    user_nick=new_user_nick
            else:
                user_nick = new_user_nick
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(changebtn, yesbtn, backbtn)
            bot.send_message(message.chat.id,
                                    text='Получается, регистрирую так? \n Мероприятие: ' + reg_event_name + ' \n Ник: ' + user_nick + ' \n Имя: ' + user_name,
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
        bot.send_message(message.chat.id, text='Получается, регистрирую так?\nМероприятие: '+reg_event_name+'\nНик: '+user_nick+'\nИмя: '+user_name, reply_markup=markup)
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
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        bot.register_next_step_handler(message, are_you, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def send_for_reg(message, reg_event_ID, reg_event_name, user_nick, user_name):
    airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_RW)
    get_registration_list()
    if reg_event_name not in get_registration_list.avalible_event_name_event_id_dict_full.keys():
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
                             text=user_nick+' зарегистрирован_а на ' + reg_event_name)
        write_in_log_regular_events(inlogtxt='@' + message.from_user.username + ' зарегистрировал_а ' + user_nick + ", " + user_name + " на " + reg_event_name)  # писька в лог
    main_menu(message)

def chose_feedack_event(message):
    airtable = Airtable(airtale_app, 'tbleWW3ENwjP0uDgh', api_key_R)
    response_feedack=airtable.get_all(view='viwZFoA68S3S4qccH')
    name_event = []
    for i in range(len(response_feedack)):
        eventday = datetime.strptime(response_feedack[i]['fields']['Date'][:len(response_feedack[i]['fields']['Date']) - 5],
                                     '%Y-%m-%dT%H:%M:%S')
        evenday = datetime(eventday.year, eventday.month, eventday.day).date()
        eventname = response_feedack[i]['fields']['Name event']
        if (date.today() - timedelta(days=10)) <= evenday <= date.today():
            name_event.append(eventname)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(name_event)):
        btn = types.KeyboardButton('"' + name_event[i] + '"')
        markup.add(btn)
    markup.add(backbtn)
    bot.send_message(message.chat.id,
                     text='Выбери мероприятие', reply_markup=markup)
    bot.register_next_step_handler(message, give_feedback, name_event)

def give_feedback(message, name_event):
    if message.text[1 : -1] in name_event:
        event_name=message.text[1 : -1]
        airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_R)
        chat_ids=[]
        nicks=''
        dis_nicks = airtable.search('Event for reg', event_name)
        for i in range(len(dis_nicks)):
            try:
                nick=dis_nicks[i]['fields']['You login in TG (reg)'].lower()
                if nick[0]!='@':
                    nick='@'+nick
                chat_ids.append(user_names_chatid_dict[nick])
                nicks += nick + ', '
            except:
                a=1
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(yesbtn, backbtn)
        bot.send_message(message.chat.id, text='Вот список получателей (если он пустой, удали запятые из названия эвентав в эйртэйбле и попробуй еще раз. Вернусь попробую пофиксить): '+nicks,reply_markup=markup)
        bot.register_next_step_handler(message, send_feedback, chat_ids, event_name, nicks)
    elif message.text=='Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
        bot.send_message(message.chat.id,
                         text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        bot.register_next_step_handler(message, give_feedback, name_event)

def send_feedback(message, chat_ids, event_name, nicks):
    if message.text=='Да':
        feedback_text = open('./feedback.txt', 'r', encoding='UTF-8').read()
        for i in range(len(chat_ids)):
            bot.send_message(chat_ids[i], text=feedback_text.replace("eventame", event_name, 1), parse_mode='Markdown', disable_web_page_preview=True)
        if message.chat.id not in chat_ids:
            bot.send_message(message.chat.id, text=feedback_text.replace("eventame", event_name, 1), parse_mode='Markdown', disable_web_page_preview=True)
        bot.send_message(message.chat.id, text='Отправил')
        write_in_log_regular_events(inlogtxt='@'+message.from_user.username.lower() + ' отправил_а запрос на фидбэк: '+nicks)
        main_menu(message)
    elif message.text=='Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
        bot.register_next_step_handler(message, send_feedback, chat_ids, event_name)

def write_feedback_at_airtale(message):
    airtable = Airtable(airtale_app, airtable_feedback_tbl, api_key_RW)
    nick=message.from_user.username
    if nick==None:
        nick='noname'
    airtable.insert(
        {you_login_in_TG_field_feedback: '@'+nick, whats_your_name_field_feedback: 'from tg bot', my_comment_field_feedback: message.text})

def error():
    try:
        bot.polling(none_stop=True, interval=0)

    except Exception as ex:
        write_in_log_error(inlogtxt=str(ex))
        error()
error()
    



























