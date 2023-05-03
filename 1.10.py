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
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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
testbtn = ty+pes.KeyboardButton("test")
regoneventbtn = types.KeyboardButton('Зарегистрироваться на мероприятие')
changenamebtn = types.KeyboardButton('Изменить имя')
changenickbtn = types.KeyboardButton('Изменить ник')
backbtn = types.KeyboardButton("Отмена")
mainmenubtn = types.KeyboardButton("Главное меню")
yesbtn = types.KeyboardButton('Да')
nobtn = types.KeyboardButton('Нет')
changebtn = types.KeyboardButton('Изменить ник или имя')
askfeedbackbtn = types.KeyboardButton('Разослать запрос фидбэка')
allaoboutsubscriptionbtn = types.KeyboardButton('Все про подписку')
readybtn = types.KeyboardButton('Готово')
sendfeedbackbtn = types.KeyboardButton('Отзыв о событии')
skipbtn = types.KeyboardButton('Пропустить')
pingbtn = types.KeyboardButton('🖕')
onetotenbtn=[]
for i in range(11):
    onetotenbtn.append(types.KeyboardButton(str(i)))
paybtn = types.KeyboardButton('Оплата')

adminlist = open('admin_list.txt', 'r', encoding='UTF-8').read().split('\n') #открываю txt со списком админов


# create dicts that coteins users nicks and all them events
user_event_names_dict = {}                      # {nick: event_name, event_name}
event_name_event_id_dict = {}                   # {event_id: event_name <-/-> event_name: event_id}
user_names_chatid_dict = {}                     # {nick: chatid <-/-> chatid: nick}
with open('user_names_chatid.pkl', 'rb') as f:  # load DB of users
    user_names_chatid_dict = pickle.load(f)
event_names_chatid_dict = {}                    # {event_name: chatid, chatid}
event_ids_for_feedback_dict={}
event_names_for_feedback_dict={}
eventList = {}                                  #словарь с персональными списками мероприятий
pnick = {}
is_user_subscribed={}
feedback_dict={}
feedback_messages_list=['О каком событии хочешь оставить отзыв?',
                        'Порекомендовал_а бы ты мероприятие своим друзьям и знакомым? Где 0 - никогда не посоветую и буду отговаривать, а 10 - буду все время звать на мероприятия.',
                        'Что понравилось на мероприятии?',
                        'Что показалось лишним или чего не хватило?',
                        'Мой комментарий',
                        'Как тебя зовут?']

what_did_you_like_list={}
def call_event_name_event_id_dict(): #{event_id: event_name <-/-> event_name: event_id}
    airtable = Airtable(airtale_app, event_tbl, api_key_R)
    response_event = airtable.get_all(view=event_future_view)
    for i in range(len(response_event)):
        event_id=response_event[i]['id']
        event_name=response_event[i]['fields']['Name event']
        event_name_event_id_dict[event_id]=event_name
        event_name_event_id_dict[event_name]=event_id

def call_user_event_names_dict():  # {nick: event_name, event_name}
    call_event_name_event_id_dict()
    airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_R)
    response_reg = airtable.get_all(view=event_for_reg_future_events_view)
    for i in range(len(response_reg)):
        try:
            user_nick=response_reg[i]['fields']['You login in TG (reg)'].lower().replace(' ','')
            if user_nick[0]!='@':
                user_nick='@'+user_nick
            user_event_id=''.join(response_reg[i]['fields']['Event for reg'])
            user_event=event_name_event_id_dict[user_event_id]
            if user_nick in user_event_names_dict.keys():
                if user_event not in user_event_names_dict[user_nick]:
                    user_event_names_dict[user_nick].append(user_event)
            else:
                user_event_names_dict[user_nick]=user_event.split('/*{}')
        except Exception as ex:
            i+=1
def call_event_names_chatid_dict(): # {event_name: chatid, chatid}\
    call_event_name_event_id_dict()
    airtable = Airtable(airtale_app, airtable_reg_tbl, api_key_R)
    response_reg = airtable.get_all(view=event_for_reg_future_events_view)
    for i in range(len(response_reg)):
        try:
            event_id=''.join(response_reg[i]['fields']['Event for reg'])
            event_name=event_name_event_id_dict[event_id]
            user_nick=response_reg[i]['fields']['You login in TG (reg)'].lower().replace(' ','')
            if user_nick[0]!='@':
                user_nick='@'+user_nick
            if user_nick in user_names_chatid_dict.keys():
                user_chat_id=user_names_chatid_dict[user_nick]
                if event_name in event_names_chatid_dict.keys():
                    if user_chat_id not in event_names_chatid_dict[event_name]:
                        event_names_chatid_dict[event_name].append(user_chat_id)
                else:
                    event_names_chatid_dict[event_name]=[]
                    event_names_chatid_dict[event_name].append(user_chat_id)
        except:
            i+=1
def call_event_for_feedback_dict():
    airtable = Airtable(airtale_app, event_tbl, api_key_R)
    response_feedack = airtable.get_all(view=event_tbl_for_feedback_view)
    for i in range(len(response_feedack)):
        eventname = response_feedack[i]['fields']['Name event']
        eventid = response_feedack[i]['id']
        event_ids_for_feedback_dict[eventid] = eventname
        event_names_for_feedback_dict[eventname] = eventid

call_event_for_feedback_dict()
call_event_names_chatid_dict()                                                #вызываю обновление БД
call_user_event_names_dict()
call_event_name_event_id_dict()
@bot.message_handler(commands=["start"])                                    #я не знаю что это(((( видимо штука которая ждёт сообщения, я хз
def Start(m):
    #первая встреча с дорогим пользователем
    nick = m.from_user.username
    if m.from_user.username == None:
        nick = 'nobody'
    write_in_log_regular_events(inlogtxt='@' + nick + ' нажал_a \start')     #писька в лог

    # call markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)                #маркап это типа список кнопок. объявляю
    markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn)  #добавляю
    if m.from_user.username in adminlist:                                   #если чел в админ листе добавляю админские кнопки
        markup.add(sendreminderbtn, testbtn, askfeedbackbtn, pingbtn)
        write_in_log_regular_events(inlogtxt='@' + m.from_user.username + ' взял_а админский доступ')                                              #писька в лог

    # send helo text
    hello_text=open(hello_txt, 'r', encoding='UTF-8').read()
    bot.send_message(m.from_user.id, text="".join(hello_text), parse_mode=ParseMode.HTML, reply_markup=markup, disable_web_page_preview=True)

    add_user(m)                                                             #добавляю юзера в свой список если его там нет

@bot.message_handler(content_types=["text"])                                #я не знаю что это(((( видимо штука которая ждёт сообщения, я хз
def handle_text(message):
    user_id = message.chat.id                                               #это айди юзера. бот общается с пользователем только по айди

    # registration check
    if message.text.strip() == 'Мои регистрации':                           #тут и дальше тект сообщения интерпритируется как команда
        if message.from_user.username is not None:
            add_user(message)
            call_user_event_names_dict()                                      #обновляю бд
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
            write_in_log_regular_events(inlogtxt='@' + message.from_user.username + ' запросил_a свои регистрции')
        else:
            bot.send_message(user_id, text="Для того чтобы проверить свои регистрации, нужно иметь ник с @")
            main_menu(message)
            write_in_log_regular_events(inlogtxt='анон запросил_a свои регистрции')              #писька в лог

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
        add_user(message)
    elif message.text.strip() == 'Все про подписку':
        aboutsubtext = open('./allaoboutsubscription.txt', 'r', encoding='UTF-8').read()              #открываю текст из файла и отправляю
        bot.send_message(message.from_user.id, text="".join(aboutsubtext), parse_mode='Markdown',
                         disable_web_page_preview=True)
        write_in_log_regular_events(inlogtxt='@' + message.from_user.username + ' узнал все про подписку')
        add_user(message)
    elif message.text.strip() == 'Отзыв о событии':
        feedback_preseting(message)
        add_user(message)

    elif message.text.strip() == '🖕':
        bot.send_message(message.chat.id, text='🖕')

    elif message.text.strip() == 'Оплата':
        bot.send_photo(message.chat.id, photo=open('donate.jpg', 'rb'), caption='Чтобы оплатить мероприятие или просто задонатить, тебе нужно нажать кнопку "Пожервовать" прикреплённую к следующему сообщению. \nПрими во внимание что в поле "Tip (Optional)" нужно ввести значение на 1€ меншье того, что ты хочешь заплатить. Ориентируйся на поле "Total", как на картинке свеху')
        bot.forward_message(message.chat.id, 214130351, donate_message_id)
#АДМИНСКИЕ ФУНКЦИИ
    elif message.text.strip() == 'Разослать запрос фидбэка' and message.from_user.username in adminlist:
        chose_feedack_event(message)                                                                                    #сразу в метод

    # rassylka
    elif message.text.strip() == 'Отправить напоминание' and message.from_user.username in adminlist:
        call_event_names_chatid_dict()                                                                  #обновил базу
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(len(list(event_names_chatid_dict.keys()))):                                  #сделал все кнопки с названиями мероприятия
            btn = types.KeyboardButton(list(event_names_chatid_dict.keys())[i])
            markup.add(btn)
        markup.add(backbtn)                                                                         #добавка кнопки назад
        send=bot.send_message(message.chat.id, text='Выбери мероприятие:', reply_markup=markup)
        bot.register_next_step_handler(send, chose_event_for_spam)                                  #жду ответа от юзера и отсылаю ответ в chose_event_for_spam


    elif message.text.strip() == 'test' and message.from_user.username=='Shkoterman':                                               #тестовая кнопка, без комментариев

        def test():
            print('test')


            #call_event_name_event_id_dict()
            #print(event_name_event_id_dict)
            #print(len(event_name_event_id_dict))

            #call_event_names_chatid_dict()
            #print(event_names_chatid_dict)
            #print(len(event_names_chatid_dict))

            #call_user_event_names_dict()
            #print(user_event_names_dict)
            #print(len(user_event_names_dict))
        test()

    else:   #когда непонял команду
        bot.send_message(message.chat.id, text='К сожалению, меня пока не научили читать😔 Если вы хотите дать обратную связь или поделиться своими мыслями - пишите @julia_sergina. Если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        try:
            nick=message.from_user.username
            if nick == None:
                nick = 'nobody'
            write_in_log_misunderstand(inlogtxt='бот не понял команды от @' + nick + ': ' + message.text)
            write_feedback_at_airtale(message,
                                      event_id=[],
                                      recomendacion=0,
                                      what_did_you_like=[],
                                      lishnee='',
                                      comment=message.text,
                                      user_name='',
                                      event_name='',
                                      misunderstand=True)
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
    markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn)
    if message.from_user.username in adminlist:
        markup.add(sendreminderbtn, testbtn, askfeedbackbtn, pingbtn)
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
    call_event_names_chatid_dict()                                          #обновляю бд
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
        markup.add(nobtn, yesbtn, mainmenubtn)
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
        call_user_event_names_dict()
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
            markup.add(mainmenubtn)
            bot.send_message(message.chat.id, text='Введи имя:', reply_markup=markup)
            bot.register_next_step_handler(message, use_new_name, reg_event_ID, reg_event_name, user_nick, user_name, markup)
        elif alreadyregistred==False:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(nobtn, yesbtn, mainmenubtn)
            bot.send_message(message.chat.id, text='Ты '+user_name+'?', reply_markup=markup)
            bot.register_next_step_handler(message, are_you, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Нет':
        types.ReplyKeyboardRemove()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(mainmenubtn)
        bot.send_message(message.chat.id, text='Введи ник:', reply_markup=markup)
        bot.register_next_step_handler(message, use_new_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Главное меню':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        bot.register_next_step_handler(message, use_your_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def use_new_username (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Главное меню':
        main_menu(message)
    elif user_name!=None:
        #registration_on_event_chek(message, reg_event_ID, reg_event_name, user_nick, user_name, markup)
        send_for_reg(message, reg_event_ID, reg_event_name, user_nick, user_name)
    elif message.text != None:
        user_nick = message.text
        if user_nick[0] != '@':
            user_nick = '@' + user_nick
        call_user_event_names_dict()
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
    if message.text == 'Главное меню':
        main_menu(message)
    elif message.text!=None:
        user_name=message.text
        send_for_reg(message, reg_event_ID, reg_event_name, user_nick, user_name)

        #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #markup.add(changebtn, yesbtn, mainmenubtn)
        #bot.send_message(message.chat.id, text='Получается, регистрирую так? \n Мероприятие: '+reg_event_name+' \n Ник: '+user_nick+' \n Имя: '+user_name, reply_markup=markup)
        #bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)
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
        markup.add(changenamebtn, changenickbtn, mainmenubtn)
        bot.send_message(message.chat.id, text='Что изменить?', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Главное меню':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo = open('wat/'+str(random.randrange(1, 6))+'.jpeg', 'rb'), reply_markup=markup)
        bot.send_message(message.chat.id, text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def change_ik_or_username (message, reg_event_ID, reg_event_name, user_nick, user_name, markup):
    if message.text == 'Изменить имя':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(mainmenubtn)
        what=0
        bot.send_message(message.chat.id, text='Введи новое имя', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username_get, reg_event_ID, reg_event_name, user_nick, user_name, what)
    elif message.text == 'Изменить ник':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(mainmenubtn)
        what=1
        bot.send_message(message.chat.id, text='Введи новый ник:', reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username_get, reg_event_ID, reg_event_name, user_nick, user_name, what)
    elif message.text == 'Главное меню':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'), reply_markup=markup)
        bot.register_next_step_handler(message, change_ik_or_username, reg_event_ID, reg_event_name, user_nick, user_name, markup)

def change_ik_or_username_get (message, reg_event_ID, reg_event_name, user_nick, user_name, what):
        if message.text == 'Главное меню':
            main_menu(message)
        elif what==0:
            user_name=message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(changebtn, yesbtn, mainmenubtn)
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
            call_user_event_names_dict()
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
            markup.add(changebtn, yesbtn, mainmenubtn)
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
        send_for_reg(message, reg_event_ID, reg_event_name, user_nick, user_name)

        #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #markup.add(changebtn, yesbtn, mainmenubtn)
        #bot.send_message(message.chat.id, text='Получается, регистрирую так?\nМероприятие: '+reg_event_name+'\nНик: '+user_nick+'\nИмя: '+user_name, reply_markup=markup)
        #bot.register_next_step_handler(message, registration_on_event_chek, reg_event_ID, reg_event_name, user_nick, user_name, markup)
    elif message.text == 'Нет':
        types.ReplyKeyboardRemove()
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(mainmenubtn)
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
        call_user_event_names_dict()
        if user_nick[0]!='@':
            user_nick='@'+user_nick
        if reg_event_name in user_event_names_dict[user_nick]:
            bot.send_message(message.chat.id,
                             text=user_nick+' зарегистрирован_а на ' + reg_event_name)
            bot.send_message(message.chat.id,
                             text='💶 Если ты регистрируешься на платное мероприятие (информация об этом есть в анонсе), ты можешь оплатить его вот тут 👇 \nhttps://revolut.me/iuliiaqj3y \nОбязательно укажи свой никнэйм из телеграма в комментарии и сохрани скриншот оплаты.', disable_web_page_preview=True)
        write_in_log_regular_events(inlogtxt='@' + message.from_user.username + ' зарегистрировал_а ' + user_nick + ", " + user_name + " на " + reg_event_name)  # писька в лог
    main_menu(message)

def chose_feedack_event(message):
    airtable = Airtable(airtale_app, event_tbl, api_key_R)
    response_feedack=airtable.get_all(view=event_tbl_for_feedback_view)
    name_event = {}
    for i in range(len(response_feedack)):
        eventname = response_feedack[i]['fields']['Name event']
        eventid = response_feedack[i]['id']
        name_event[eventname]=eventid
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(name_event.keys())):
        btn = types.KeyboardButton('"' + list(name_event.keys())[i] + '"')
        markup.add(btn)
    markup.add(backbtn)
    bot.send_message(message.chat.id,
                     text='Выбери мероприятие', reply_markup=markup)
    bot.register_next_step_handler(message, give_feedback, name_event)

def give_feedback(message, name_event):
    if message.text[1 : -1] in name_event.keys():
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
        markup.add(yesbtn, mainmenubtn)
        bot.send_message(message.chat.id, text='Вот список получателей (если он пустой, удали запятые из названия эвентав в эйртэйбле и попробуй еще раз. Вернусь попробую пофиксить): '+nicks,reply_markup=markup)
        event_id = name_event[event_name]
        bot.register_next_step_handler(message, send_feedback, chat_ids, event_name, event_id, nicks)
    elif message.text=='Отмена':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
        bot.send_message(message.chat.id,
                         text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
        bot.register_next_step_handler(message, give_feedback, name_event)

def send_feedback(message, chat_ids, event_name, event_id, nicks):
    if message.text=='Да':
        feedback_text = open('./feedback.txt', 'r', encoding='UTF-8').read()

        markup=InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton('Оставить отзыв '+event_name, callback_data='05/*/'+event_id))

        for i in range(len(chat_ids)):
            bot.send_message(chat_ids[i], text=feedback_text.replace("eventame", event_name, 1), parse_mode='Markdown', disable_web_page_preview=True, reply_markup=markup)
        if message.chat.id not in chat_ids:
            bot.send_message(message.chat.id, text=feedback_text.replace("eventame", event_name, 1), parse_mode='Markdown', disable_web_page_preview=True, reply_markup=markup)
        bot.send_message(message.chat.id, text='Отправил')
        write_in_log_regular_events(inlogtxt='@'+message.from_user.username.lower() + ' отправил_а запрос на фидбэк: '+nicks)
        main_menu(message)
    elif message.text=='Главное меню':
        main_menu(message)
    else:
        bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
        bot.register_next_step_handler(message, send_feedback, chat_ids, event_name, event_id, nicks)
def feedback_preseting(message):
    feedback_dict[message.chat.id] = {'event_id': str,
                                      'recomendacion': int,
                                      'what_did_you_like': list,
                                      'lishnee': str,
                                      'comment': str,
                                      'user_name': str,
                                      'event_name': str}
    call_event_for_feedback_dict()
    name_event=event_names_for_feedback_dict
    if message.from_user.username is not None and message.chat.id in user_names_chatid_dict:
        find_it(message.from_user.username)
        feedback_dict[message.chat.id]['user_name'] = find_it.user_name
    feedback(message, name_event, step=0, value=None)
def feedback(message, name_event, step, value):
    if value is not None and step<=len(list(feedback_dict[message.chat.id].keys())):
        feedback_dict[message.chat.id][list(feedback_dict[message.chat.id].keys())[step]]=value
        value=None
    if step==len(list(feedback_dict[message.chat.id].keys()))-1:
        bot.send_message(message.chat.id,text='Спасибо за твой отзыв!!! Мы ценим такое и будем стараться быть лучше!')
        main_menu(message)
        try:
            write_feedback_at_airtale(message,
                                      event_id=feedback_dict[message.chat.id]['event_id'].split(),
                                      recomendacion=int(feedback_dict[message.chat.id]['recomendacion']),
                                      what_did_you_like=feedback_dict[message.chat.id]['what_did_you_like'],
                                      lishnee=feedback_dict[message.chat.id]['lishnee'],
                                      comment=feedback_dict[message.chat.id]['comment'],
                                      user_name=feedback_dict[message.chat.id]['user_name'],
                                      event_name=feedback_dict[message.chat.id]['event_name'],
                                      misunderstand=False)
        except Exception as ex:
            print(ex)
    else:
        step_value=feedback_dict[message.chat.id][list(feedback_dict[message.chat.id].keys())[step]]
        if type(step_value) is type:  # проверили, что пустой если да иду спрашивать
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if step == 0:
                for i in range(len(name_event)):
                    btn = types.KeyboardButton(list(name_event.keys())[i])
                    markup.add(btn)
                markup.add(backbtn)
                send = bot.send_message(message.chat.id, text=feedback_messages_list[step], reply_markup=markup)
                bot.register_next_step_handler(send, feedback_steps, name_event, step)
            elif step == 2:
                markup.add(mainmenubtn, readybtn)
                bot.send_message(message.chat.id, text=feedback_messages_list[step], reply_markup=markup)
                what_did_you_like_list[message.chat.id] = ['➖Формат', '➖Площадка', '➖Атмосфера', '➖Организация',
                                                           '➖Люди']
                feedback_like_list(message, first=True)
            else:
                if step == 1:
                    markup.add(onetotenbtn[0],
                               onetotenbtn[1],
                               onetotenbtn[2],
                               onetotenbtn[3],
                               onetotenbtn[4],
                               onetotenbtn[5],
                               onetotenbtn[6],
                               onetotenbtn[7],
                               onetotenbtn[8],
                               onetotenbtn[9],
                               onetotenbtn[10],
                               mainmenubtn)
                else:
                    markup.add(mainmenubtn, skipbtn)
                send = bot.send_message(message.chat.id, text=feedback_messages_list[step], reply_markup=markup)
                bot.register_next_step_handler(send, feedback_steps, name_event, step)
        elif type(step_value) is not type:  # если нет то просто добавляю
            step += 1
            feedback(message, name_event, step, value)

def feedback_steps(message, name_event, step):
        if message.text=='Главное меню' or message.text=='Отмена':
            main_menu(message)
        elif step == 0:
            if message.text in name_event.keys():
                value=name_event[message.text]
                feedback_dict[message.chat.id]['event_name']=message.text
                feedback(message, name_event, step, value=value)
            else:
                bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
                bot.send_message(message.chat.id,
                                 text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу или ввода текста, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
                bot.register_next_step_handler(message, feedback_steps, name_event, step)
        elif step== 1:
            try:
                if 0<=int(message.text)<=10:
                    value = message.text
                    feedback(message, name_event, step, value=value)
                else:
                    send = bot.send_message(message.chat.id, text='Оценка должны быть целым числом от 0 до 10 включительно')
                    bot.register_next_step_handler(send, feedback_steps, name_event, step=step)
            except:
                send = bot.send_message(message.chat.id, text='Оценка должны быть целым числом от 0 до 10 включительно')
                bot.register_next_step_handler(send, feedback_steps, name_event, step=step)
        elif step==2:
            if message.text == 'Готово':
                i=len(what_did_you_like_list[message.chat.id])-1
                while i>=0:
                    if what_did_you_like_list[message.chat.id][i][0]=='✅':
                        what_did_you_like_list[message.chat.id][i]=what_did_you_like_list[message.chat.id][i][1:]
                    else:
                        what_did_you_like_list[message.chat.id].pop(i)
                    i-=1
                value=what_did_you_like_list[message.chat.id]
                what_did_you_like_list[message.chat.id]=[]
                feedback(message, name_event, step, value)
            else:
                bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
                bot.send_message(message.chat.id,
                                 text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу или ввода текста, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
                bot.register_next_step_handler(message, feedback_steps, name_event, step)
        elif message.text=='Пропустить' and step == 3 or step == 4 or step == 5:
            feedback(message, name_event, step, value='-')
        else:
            value=message.text
            if value==None:
                bot.send_photo(message.chat.id, photo=open('wat/' + str(random.randrange(1, 6)) + '.jpeg', 'rb'))
                bot.send_message(message.chat.id,
                                 text='Я не понимаю такой ответ, кажется я жду от тебя нажатия на кнопку внизу или ввода текста, однако, если я веду себя странно, реагирую неадекватно - перезаусти меня командой /start')
            feedback(message, name_event, step, value=value)
def feedback_like_list(message, first):
    markup=InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(what_did_you_like_list[message.chat.id][0], callback_data='00'),
               InlineKeyboardButton(what_did_you_like_list[message.chat.id][1], callback_data='01'),
               InlineKeyboardButton(what_did_you_like_list[message.chat.id][2], callback_data='02'),
               InlineKeyboardButton(what_did_you_like_list[message.chat.id][3], callback_data='03'),
               InlineKeyboardButton(what_did_you_like_list[message.chat.id][4], callback_data='04'),
               )
    if first:
        send=bot.send_message(message.chat.id, text='Можно выбрать несколько:', reply_markup=markup)
        bot.register_next_step_handler(send, feedback_steps, name_event=[], step=2)
    else:
        bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=markup)
def fast():
    print('asdasdasdasasdasasaszxczxczxc')
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    call_data=call.data.split('/*/')
    btnnumber=int(call_data[0])
    if 0<=btnnumber<=4:
        if what_did_you_like_list[call.message.chat.id][btnnumber][0]=='➖':
            what_did_you_like_list[call.message.chat.id][btnnumber] = what_did_you_like_list[call.message.chat.id][btnnumber][1:]
            what_did_you_like_list[call.message.chat.id][btnnumber] = '✅' +what_did_you_like_list[call.message.chat.id][btnnumber]
            feedback_like_list(call.message, first=False)
        else:
            what_did_you_like_list[call.message.chat.id][btnnumber] = what_did_you_like_list[call.message.chat.id][btnnumber][1:]
            what_did_you_like_list[call.message.chat.id][btnnumber] = '➖' + what_did_you_like_list[call.message.chat.id][btnnumber]
            feedback_like_list(call.message, first=False)
    elif btnnumber == 5:
        find_it(call.from_user.username)
        user_name = find_it.user_name
        call_event_for_feedback_dict()
        event_name=event_ids_for_feedback_dict[call_data[1]]
        feedback_dict[call.message.chat.id] = {'event_id': call_data[1],
                                          'recomendacion': int,
                                          'what_did_you_like': list,
                                          'lishnee': str,
                                          'comment': str,
                                          'user_name': str,
                                          'event_name': event_name}
        if user_name is not None:
            feedback_dict[call.message.chat.id]['user_name']=user_name
        feedback(message=call.message, name_event=call_data[1], step=0, value=None)

def write_feedback_at_airtale(message, event_id, recomendacion, what_did_you_like, lishnee, comment, user_name, event_name, misunderstand):
    airtable = Airtable(airtale_app, airtable_feedback_tbl, api_key_RW)
    if recomendacion==0:
        recomendacion=None

    if message.from_user.username==None:
        nick='noname'
    else:
        nick = '@' + message.from_user.username.lower()
    airtable.insert({
        you_login_in_TG_field_feedback: nick,
        name_event_field_feedback: event_id,
        recomendacion_field_feedback: recomendacion,
        what_did_you_like_field_feedback: what_did_you_like,
        lishnee_field_feedback: lishnee,
        commet_field_feedback: comment,
        whats_your_name_field_feedback: user_name,
    })
    if misunderstand==False:
        write_in_log_regular_events(inlogtxt=nick + ' дал_а ОС про мероприятие ' + event_name)
def error():
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
        #bot.polling(none_stop=True, interval=0)

    except Exception as ex:
        write_in_log_error(inlogtxt=str(ex))
        bot.send_message(214130351, text='estoy cayendo! \n'+str(ex))
        error()
error()