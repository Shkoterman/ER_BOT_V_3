import ER_DB
import btns
import strs
import telebot
from telebot import types

bot = telebot.TeleBot('5865283503:AAHI8sUoRRzDh3d0w1TpNnY35ymAqDTv5A4')  # this is test
# bot = telebot.TeleBot('5806434689:AAG383Pr1XxSpl4vjJ9rNFR27xJJA19bs0g')  # this is prod

what_did_you_like_list = {}


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if what_did_you_like_list[call.from_user.id][int(call.data)][0] == '➖':
        what_did_you_like_list[call.from_user.id][int(call.data)] = '✔ ' + what_did_you_like_list[call.from_user.id][
                                                                               int(call.data)][1:]
    elif what_did_you_like_list[call.from_user.id][int(call.data)][0] == '✔':
        what_did_you_like_list[call.from_user.id][int(call.data)] = '➖ ' + what_did_you_like_list[call.from_user.id][
                                                                               int(call.data)][1:]
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(what_did_you_like_list[call.from_user.id][0], callback_data='00'),
               types.InlineKeyboardButton(what_did_you_like_list[call.from_user.id][1], callback_data='01'),
               types.InlineKeyboardButton(what_did_you_like_list[call.from_user.id][2], callback_data='02'),
               types.InlineKeyboardButton(what_did_you_like_list[call.from_user.id][3], callback_data='03'),
               types.InlineKeyboardButton(what_did_you_like_list[call.from_user.id][4], callback_data='04'))
    bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=markup)


@bot.message_handler(commands=["start"])  # я не знаю что это(((( видимо штука которая ждёт сообщения, я хз
def Start(message):
    main_menu(message, True)
    ER_DB.add_new_user(message.from_user.username, message.chat.id)


@bot.message_handler(content_types=["text"])  # я не знаю что это(((( видимо штука которая ждёт сообщения, я хз
def handle_text(message):
    # юзерские функции
    if message.text == btns.myregistrationbtn.text:
        check_registration(message)
    if message.text == btns.regoneventbtn.text:
        registration_step_1(message)
    if message.text == btns.sendfeedbackbtn.text:
        feedback_step_1(message)
    if message.text == btns.allaoboutsubscriptionbtn.text:
        bot.send_message(message.chat.id, text=strs.all_about_sub, disable_web_page_preview=True, parse_mode='Markdown')
    if message.text == btns.paybtn.text:
        bot.send_message(message.chat.id, text=strs.payment_text_info, disable_web_page_preview=True,
                         parse_mode='Markdown')
        bot.forward_message(message.chat.id, 214130351, 9582)
    if message.text == btns.pingbtn.text:
        bot.send_message(message.chat.id, text=btns.pingbtn.text)
    if message.text == btns.cancel.text:
        pass

    # админские функции
    if message.text == btns.sendreminderbtn.text and message.from_user.username in ER_DB.get_admin_list():
        send_reminder_step_1(message)
    if message.text == btns.askfeedbackbtn.text and message.from_user.username in ER_DB.get_admin_list():
        send_feedback_request_step_1(message)

    # сугубо мои
    if message.text == btns.testbtn.text and message.chat.id == 214130351:
        ER_DB.for_cancel_reg_event_list(message.from_user.username)


def main_menu(message, frsttime):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.chat.id == 214130351:
        markup = btns.my_main_menu_markup

    elif message.from_user.username in ER_DB.get_admin_list():
        markup = btns.admin_main_menu_markup

    else:
        markup = btns.user_main_menu_markup

    if frsttime == 1:
        text = strs.hello_text
    elif frsttime == 2:
        text = strs.time_out_text
    else:
        text = strs.main_menu_text
    bot.send_message(message.chat.id, text=text, reply_markup=markup)


def check_registration(message):
    if message.from_user.username == None:
        bot.send_message(message.chat.id, text=strs.need_dog_msg)
    else:
        reg_event_lists = ER_DB.for_reg_event_list(message.from_user.username)
        if reg_event_lists == ([], []):
            bot.send_message(message.chat.id, text=strs.no_reg_events_msg)
        if reg_event_lists[0] != []:
            reply_text = strs.resgistred_msg_text + '\n'.join(reg_event_lists[0])
            bot.send_message(message.chat.id, text=reply_text)
        if reg_event_lists[1] != []:
            reply_text = strs.resgistred_in_WL_msg_text + '\n'.join(reg_event_lists[1])
            bot.send_message(message.chat.id, text=reply_text)


def registration_step_1(message):
    if message.from_user.username == None:
        bot.send_message(message.chat.id, text=strs.need_dog_msg)
    else:
        open_for_reg_events = ER_DB.open_for_reg_events()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(len(open_for_reg_events.keys())):
            markup.add(types.KeyboardButton(list(open_for_reg_events.keys())[i]))
        markup.add(btns.backbtn)

        if bot.get_chat_member(-1001855787678, message.chat.id).status != 'left':  # 966176056
            user_is_sub = True
        else:
            user_is_sub = False
        for_reg_dickt = {'event_id': str,
                         'user_nick': '@' + message.from_user.username.lower(),
                         'user_name': str,
                         'user_is_sub': user_is_sub,
                         'ev_is_sub': bool,
                         'reg_in_WL': bool,
                         'plus_one': False,
                         'first_time': False}
        send = bot.send_message(message.chat.id, text=strs.here_is_events, reply_markup=markup)
        bot.register_next_step_handler(send, registration_step_2, for_reg_dickt, open_for_reg_events)


def registration_step_2(message, for_reg_dickt, open_for_reg_events):
    if message.text in open_for_reg_events.keys():
        if '@' + message.from_user.username.lower() in ER_DB.tgnicks_of_event_R_and_WL(
                open_for_reg_events[message.text][0]):
            bot.send_message(message.chat.id, text=strs.already_registred)
            main_menu(message, 0)
        else:
            if message.text in open_for_reg_events.keys():
                for_reg_dickt['event_id'] = open_for_reg_events[message.text][0]
                for_reg_dickt['reg_in_WL'] = open_for_reg_events[message.text][1]
                for_reg_dickt['ev_is_sub'] = open_for_reg_events[message.text][2]
                for_reg_dickt['user_name'] = ER_DB.get_user_name(message.from_user.username)

                if for_reg_dickt['ev_is_sub'] == True and for_reg_dickt['user_is_sub'] == False:
                    bot.send_message(message.chat.id, text=strs.you_have_no_sub)
                    main_menu(message, 0)
                elif for_reg_dickt['user_name'] == None:
                    markup = types.ReplyKeyboardRemove()
                    send = bot.send_message(message.chat.id, text=strs.whats_your_name, reply_markup=markup)
                    bot.register_next_step_handler(send, registration_step_3, for_reg_dickt)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(btns.minusonebtn, btns.backbtn,
                                                                                 btns.plusonebtn)
                    send = bot.send_message(message.chat.id, text=strs.plus_one_message, reply_markup=markup)
                    bot.register_next_step_handler(send, registration_step_4, for_reg_dickt)
    elif message.text == btns.backbtn.text:
        main_menu(message, 0)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(send, registration_step_2, for_reg_dickt, open_for_reg_events)


def registration_step_3(message, for_reg_dickt):
    if message.text != None:
        for_reg_dickt['user_name'] = message.text
        for_reg_dickt['first_time'] = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(btns.minusonebtn, btns.mainmenubtn,
                                                                     btns.plusonebtn)
        send = bot.send_message(message.chat.id, text=strs.plus_one_message, reply_markup=markup)
        bot.register_next_step_handler(send, registration_step_4, for_reg_dickt)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(send, registration_step_3, for_reg_dickt)


def registration_step_4(message, for_reg_dickt):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text == btns.plusonebtn.text or message.text == btns.minusonebtn.text:
        for_reg_dickt['plus_one'] = message.text == btns.plusonebtn.text
        bot.send_message(message.chat.id, text=strs.wait)
        registration_step_5(message, for_reg_dickt)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(send, registration_step_4, for_reg_dickt)


def registration_step_5(message, for_reg_dickt):
    bot.send_message(message.chat.id, text=strs.got_it)
    bot.send_message(message.chat.id, text=strs.payment_text_after_reg, disable_web_page_preview=True)
    bot.forward_message(message.chat.id, 214130351, 9582)
    main_menu(message, 0)
    if not ER_DB.add_reg(for_reg_dickt):
        bot.send_message(214130351, text=strs.rega_ne_proshla + str(for_reg_dickt))


def feedback_step_1(message):
    feedback_dickt = {'event_id': str,
                      'user_nick': '@' + str(message.from_user.username).lower(),
                      'recomendacion': int,
                      'what_did_you_like': list,
                      'unwanted': str,
                      'comment': str,
                      'user_name': str,
                      }
    ev_list = ER_DB.for_feedback_events()
    markap = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(ev_list)):
        markap.add(types.KeyboardButton(list(ev_list.keys())[i]))
    markap.add(btns.backbtn)
    send = bot.send_message(message.chat.id, text=strs.here_events_for_feedback, reply_markup=markap)
    bot.register_next_step_handler(send, feedback_step_2, feedback_dickt, ev_list)


def feedback_step_2(message, feedback_dickt, ev_list):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text not in ev_list.keys():
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(send, feedback_step_2, feedback_dickt, ev_list)
    elif message.text in ev_list.keys():
        feedback_dickt['event_id'] = ev_list[message.text]
        markap = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(11):
            markap.add(types.KeyboardButton(i))
        markap.add(btns.backbtn)
        send = bot.send_message(message.chat.id, text=strs.mark_the_event, reply_markup=markap)
        bot.register_next_step_handler(send, feedback_step_3, feedback_dickt)


def feedback_step_3(message, feedback_dickt):
    mark_is_mark = False
    try:
        feedback_dickt['recomendacion'] = int(message.text)
        if 0 <= feedback_dickt['recomendacion'] <= 10:
            mark_is_mark = True
    except:
        pass

    if message.text == btns.backbtn.text:
        main_menu(message, 0)

    elif mark_is_mark == False:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(send, feedback_step_3, feedback_dickt)
    else:

        what_did_you_like_list[message.chat.id] = ['➖Формат', '➖Площадка', '➖Атмосфера', '➖Организация', '➖Люди']
        markup1 = types.InlineKeyboardMarkup()
        markup1.row_width = 1
        markup1.add(types.InlineKeyboardButton(what_did_you_like_list[message.chat.id][0], callback_data='00'),
                    types.InlineKeyboardButton(what_did_you_like_list[message.chat.id][1], callback_data='01'),
                    types.InlineKeyboardButton(what_did_you_like_list[message.chat.id][2], callback_data='02'),
                    types.InlineKeyboardButton(what_did_you_like_list[message.chat.id][3], callback_data='03'),
                    types.InlineKeyboardButton(what_did_you_like_list[message.chat.id][4], callback_data='04'))

        markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup2.add(btns.backbtn, btns.readybtn)

        bot.send_message(message.chat.id, text=strs.what_did_u_like, reply_markup=markup2)
        send = bot.send_message(message.chat.id, text=strs.may_choose_more, reply_markup=markup1)
        bot.register_next_step_handler(send, feedback_step_4, feedback_dickt, what_did_you_like_list[message.chat.id])


def feedback_step_4(message, feedback_dickt, what_did_you_like_list):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text == btns.readybtn.text:
        feedback_dickt['what_did_you_like'] = []
        for i in range(len(what_did_you_like_list)):
            if what_did_you_like_list[i][0] == '✔':
                feedback_dickt['what_did_you_like'].append(what_did_you_like_list[i][2:])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btns.backbtn, btns.skipbtn)
        send = bot.send_message(message.chat.id, text=strs.whats_unwanted, reply_markup=markup)
        bot.register_next_step_handler(send, feedback_step_5, feedback_dickt)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(send, feedback_step_4, feedback_dickt, what_did_you_like_list)


def feedback_step_5(message, feedback_dickt):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text != None:
        feedback_dickt['unwanted'] = message.text
        send = bot.send_message(message.chat.id, text=strs.my_comment)
        bot.register_next_step_handler(send, feedback_step_6, feedback_dickt)

    elif message.text == None:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(send, feedback_step_5, feedback_dickt)


def feedback_step_6(message, feedback_dickt):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text != None:
        feedback_dickt['comment'] = message.text
        bot.send_message(message.chat.id, text=strs.thx_for_feedback)
        main_menu(message, 0)
        try:
            feedback_dickt['user_name'] = ER_DB.get_user_name(feedback_dickt['user_nick'])
        except:
            pass
        ER_DB.add_feedback(feedback_dickt)

    elif message.text == None:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(send, feedback_step_6, feedback_dickt)


def send_reminder_step_1(message):
    ev_list = ER_DB.for_reminder_events()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(ev_list)):
        markup.add(types.KeyboardButton(list(ev_list.keys())[i]))
    markup.add(btns.backbtn)
    send = bot.send_message(message.chat.id, text=strs.choose_event_for_request, reply_markup=markup)
    bot.register_next_step_handler(send, send_reminder_step_2, ev_list)


def send_reminder_step_2(messsage, ev_list):
    if messsage.text == btns.backbtn.text:
        main_menu(messsage, 0)

    elif messsage.text in ev_list.keys():
        ev_id = ev_list[messsage.text]
        spam_nick_list = ER_DB.tgnicks_of_event_R(ev_id)
        spam_id_list = ER_DB.find_user_id_or_nick(spam_nick_list)
        spam_nick_list = ER_DB.find_user_id_or_nick(spam_id_list)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btns.backbtn)
        send = bot.send_message(messsage.chat.id, text=strs.write_text, reply_markup=markup)
        bot.register_next_step_handler(send, send_reminder_step_3, spam_nick_list, spam_id_list)
    else:
        send = bot.send_message(messsage.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(messsage, send_reminder_step_2, ev_list)


def send_reminder_step_3(message, spam_nick_list, spam_id_list):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    else:
        message_for_spam_id = message.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btns.backbtn, btns.yesbtn)
        bot.send_message(message.chat.id, text=strs.this_message)
        bot.forward_message(message.chat.id, message.chat.id, message_for_spam_id)
        bot.send_message(message.chat.id, text=strs.thees_people)
        send = bot.send_message(message.chat.id, text=', '.join(spam_nick_list), reply_markup=markup)
        bot.register_next_step_handler(send, send_reminder_step_4, spam_id_list, message_for_spam_id)


def send_reminder_step_4(message, spam_id_list, message_for_spam_id):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text == btns.yesbtn.text:
        count = 0
        for i in range(len(spam_id_list)):
            try:
                bot.forward_message(spam_id_list[i], message.chat.id, message_for_spam_id)
                count += 1
            except:
                pass
        bot.send_message(message.chat.id, text=strs.request_send + str(count) + '/' + str(len(spam_id_list)))
        main_menu(message, 0)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(message, send_reminder_step_4, spam_id_list, message_for_spam_id)


def send_feedback_request_step_1(message):
    ev_list = ER_DB.for_feedback_events()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(ev_list)):
        markup.add(types.KeyboardButton(list(ev_list.keys())[i]))
    markup.add(btns.backbtn)
    send = bot.send_message(message.chat.id, text=strs.here_events_for_feedback, reply_markup=markup)
    bot.register_next_step_handler(send, send_feedback_request_step_2, ev_list)


def send_feedback_request_step_2(message, ev_list):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text in list(ev_list.keys()):
        ev_id = ev_list[message.text]
        spam_nick_list = ER_DB.tgnicks_of_event_R(ev_id)
        spam_id_list = ER_DB.find_user_id_or_nick(spam_nick_list)
        spam_nick_list = ER_DB.find_user_id_or_nick(spam_id_list)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btns.backbtn)
        send = bot.send_message(message.chat.id, text=strs.write_text, reply_markup=markup)
        bot.register_next_step_handler(send, send_feedback_request_step_3, spam_id_list, spam_nick_list)

    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(message, send_feedback_request_step_2, ev_list)


def send_feedback_request_step_3(message, spam_id_list, spam_nick_list):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    else:
        message_for_spam_id = message.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btns.backbtn, btns.yesbtn)
        bot.send_message(message.chat.id, text=strs.this_message)
        bot.forward_message(message.chat.id, message.chat.id, message_for_spam_id)
        bot.send_message(message.chat.id, text=strs.thees_people)
        send = bot.send_message(message.chat.id, text=', '.join(spam_nick_list), reply_markup=markup)
        bot.register_next_step_handler(send, send_feedback_request_step_4, spam_id_list, message_for_spam_id)


def send_feedback_request_step_4(message, spam_id_list, message_for_spam_id):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text == btns.yesbtn.text:
        count = 0
        for i in range(len(spam_id_list)):
            try:
                bot.forward_message(spam_id_list[i], message.chat.id, message_for_spam_id)
                count += 1
            except:
                pass
        bot.send_message(message.chat.id, text=strs.request_send + str(count) + '/' + str(len(spam_id_list)))
        main_menu(message, 0)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(message, send_reminder_step_4, spam_id_list, message_for_spam_id)


def cancel_reg_step_1(message):
    if message.from_user.username == None:
        bot.send_message(message.chat.id, text=strs.need_dog_msg)
    else:
        ev_list = ER_DB.for_cancel_reg_event_list(message.from_user.username)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(len(ev_list)):
            markup.add(types.KeyboardButton(list(ev_list.keys())[i]))
        markup.add(btns.backbtn)
        send = bot.send_message(message.chat.id, text=strs.what_for_cance, reply_markup=markup)
        bot.register_next_step_handler(message, cancel_reg_step_2, ev_list)


def cancel_reg_step_2(message, ev_list):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text in list(ev_list):
        event_id = ER_DB.get_event_name()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btns.backbtn, btns.skipbtn)
        send = bot.send_message(message.chat.id, text=strs.why_are_u_cancel, reply_markup=markup)
        bot.edit_message_reply_markup(send, cancel_reg_step_3, event_id)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it)
        bot.register_next_step_handler(message, cancel_reg_step_2, ev_list)


def cancel_reg_step_3(message, event_id):
    print(message.text)
    print(event_id)


bot.infinity_polling(timeout=30, long_polling_timeout=15)
