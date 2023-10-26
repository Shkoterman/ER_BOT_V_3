import ER_DB
import btns
import strs
import telebot
import time
import asyncio
from telebot import types
from datetime import datetime


test_mode=False
#test_mode=True

shkoterman_chat_id = 214130351
julia_chat_id = 346459053
if test_mode:
    payment_message_id=9582
    all_about_sub_message_id=57463
    bot = telebot.TeleBot('5865283503:AAHI8sUoRRzDh3d0w1TpNnY35ymAqDTv5A4')  # this is test
else:
    payment_message_id=9582
    all_about_sub_message_id=57463
    bot = telebot.TeleBot('5806434689:AAG383Pr1XxSpl4vjJ9rNFR27xJJA19bs0g')  # this is prod

what_did_you_like_list = {}
time_out={}

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if '00'<=call.data<='04':
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
    elif call.data=='05':
        bot.clear_step_handler(call.message)
        main_menu(call.message, 0)


def send_julia(str):
    bot.send_message(julia_chat_id, text=str)


def main_menu(message, case):
    #print(message.from_user.username)
    #print('-------------')
    #print(ER_DB.get_admin_list())
    time_out[message.chat.id] = 0
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.chat.id == shkoterman_chat_id:
        markup = btns.my_main_menu_markup
    elif message.from_user.username in ER_DB.get_admin_list():
        markup = btns.admin_main_menu_markup
    else:
        markup = btns.user_main_menu_markup
    if case == 1:
        text = strs.hello_text
        write_in_log(message, 'came with frsttime == 1')
    elif case == 2:
        text = strs.time_out_text
        bot.clear_step_handler_by_chat_id(message.chat.id)
        write_in_log(message, 'got timeout')
    elif case==3:
        text = strs.main_menu_text
    else:
        text = strs.main_menu_text
        write_in_log(message, 'pressed Cancel or got deny')

    bot.send_message(message.chat.id, text=text, reply_markup=markup)


def check_registration(message):
    write_in_log(message, 'checked registration')
    if message.from_user.username == None:
        bot.send_message(message.chat.id, text=strs.need_dog_msg)
        main_menu(message, 0)
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
    markup=types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, text=strs.wait, reply_markup=markup)
    write_in_log(message, 'begun registration')
    if message.from_user.username == None:
        bot.send_message(message.chat.id, text=strs.need_dog_msg)
        main_menu(message, 0)
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
                         'ev_is_free': False,
                         'reg_in_WL': bool,
                         'plus_one': False,
                         'first_time': False}
        send = bot.send_message(message.chat.id, text=strs.here_is_events, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview=True)
        bot.register_next_step_handler(send, registration_step_2, for_reg_dickt, open_for_reg_events)


def registration_step_2(message, for_reg_dickt, open_for_reg_events):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, text=strs.wait, reply_markup=markup)
    if message.text in open_for_reg_events.keys():
        write_in_log(message, 'tried to reg on '+message.text)
        if '@' + message.from_user.username.lower() in ER_DB.tgnicks_of_event_R_and_WL(
                open_for_reg_events[message.text][0]):
            bot.send_message(message.chat.id, text=strs.already_registred)
            main_menu(message, 0)
        else:
            if message.text in open_for_reg_events.keys():

                for_reg_dickt['event_id'] = open_for_reg_events[message.text][0]
                for_reg_dickt['reg_in_WL'] = open_for_reg_events[message.text][1]
                for_reg_dickt['ev_is_sub'] = open_for_reg_events[message.text][2]
                for_reg_dickt['ev_is_free'] = open_for_reg_events[message.text][3]
                for_reg_dickt['user_name'] = ER_DB.get_user_name(message.from_user.username)
                if for_reg_dickt['ev_is_sub'] == True and for_reg_dickt['user_is_sub'] == False:
                    bot.send_message(message.chat.id, text=strs.you_have_no_sub, disable_web_page_preview=True, parse_mode='Markdown')
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
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
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
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
        bot.register_next_step_handler(send, registration_step_3, for_reg_dickt)


def registration_step_4(message, for_reg_dickt):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text == btns.plusonebtn.text or message.text == btns.minusonebtn.text:
        for_reg_dickt['plus_one'] = message.text == btns.plusonebtn.text
        bot.send_message(message.chat.id, text=strs.wait)
        registration_step_5(message, for_reg_dickt)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
        bot.register_next_step_handler(send, registration_step_4, for_reg_dickt)


def registration_step_5(message, for_reg_dickt):
    if for_reg_dickt['reg_in_WL']:
        bot.send_message(message.chat.id, text=strs.reg_in_wl_text)
    elif for_reg_dickt['ev_is_free']:
        bot.send_message(message.chat.id, text=strs.got_it)
    else:
        bot.send_message(message.chat.id, text=strs.got_it)
        bot.send_message(message.chat.id, text=strs.payment_text_after_reg, disable_web_page_preview=True, parse_mode='Markdown')
    write_in_log(message, 'send for registration: '+str(for_reg_dickt))
    main_menu(message, 3)
    ER_DB.add_new_user(message.from_user.username, message.chat.id)
    if not ER_DB.add_reg(for_reg_dickt):
        bot.send_message(shkoterman_chat_id, text=strs.rega_ne_proshla + str(for_reg_dickt))


def feedback_step_1(message):
    ev_list = ER_DB.for_feedback_events()

    write_in_log(message, 'pressed give feedback')
    feedback_dickt = {'event_id': str,
                      'user_nick': '@' + str(message.from_user.username).lower(),
                      'recomendacion': int,
                      'what_did_you_like': list,
                      'unwanted': str,
                      'comment': str,
                      'user_name': str,
                      }

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
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
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
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
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
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
        bot.register_next_step_handler(send, feedback_step_4, feedback_dickt, what_did_you_like_list)


def feedback_step_5(message, feedback_dickt):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text != None:
        feedback_dickt['unwanted'] = message.text
        send = bot.send_message(message.chat.id, text=strs.my_comment)
        bot.register_next_step_handler(send, feedback_step_6, feedback_dickt)

    elif message.text == None:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
        bot.register_next_step_handler(send, feedback_step_5, feedback_dickt)


def feedback_step_6(message, feedback_dickt):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text != None:
        feedback_dickt['comment'] = message.text
        bot.send_message(message.chat.id, text=strs.thx_for_feedback)
        main_menu(message, 3)
        try:
            feedback_dickt['user_name'] = ER_DB.get_user_name(feedback_dickt['user_nick'])
        except:
            pass
        write_in_log(message, 'gave feedback: '+str(feedback_dickt))
        ER_DB.add_feedback(feedback_dickt)

    elif message.text == None:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
        bot.register_next_step_handler(send, feedback_step_6, feedback_dickt)


def send_reminder_step_1(message):
    ev_list = ER_DB.for_reminder_events()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(ev_list)):
        markup.add(types.KeyboardButton(list(ev_list.keys())[i]))
    markup.add(btns.backbtn)
    send = bot.send_message(message.chat.id, text=strs.choose_event_for_reminder, reply_markup=markup)
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
        send = bot.send_message(messsage.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
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
        bot.send_message(message.chat.id, text=strs.reminser_sent + str(count) + '/' + str(len(spam_id_list)))
        main_menu(message, 0)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
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
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
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
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
        bot.register_next_step_handler(message, send_reminder_step_4, spam_id_list, message_for_spam_id)


def cancel_reg_step_1(message):
    write_in_log(message, 'pressed cancel event reg')
    if message.from_user.username == None:
        bot.send_message(message.chat.id, text=strs.need_dog_msg)
    else:
        ev_list = ER_DB.for_cancel_reg_event_list(message.from_user.username)
        if ev_list=={}:
            bot.send_message(message.chat.id, text=strs.no_cancelebl_events_msg)
            main_menu(message, 0)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in range(len(ev_list)):
                markup.add(types.KeyboardButton(list(ev_list.keys())[i]))
            markup.add(btns.backbtn)
            send = bot.send_message(message.chat.id, text=strs.what_for_cance, reply_markup=markup)
            bot.register_next_step_handler(message, cancel_reg_step_2, ev_list)


def cancel_reg_step_2(message, ev_list):
    if message.text == btns.backbtn.text:
        main_menu(message, 0)
    elif message.text in list(ev_list.keys()):
        write_in_log(message, 'want to cancel ' + message.text)
        if  ev_list[message.text][1]==1:
            bot.send_message(message.chat.id, text=strs.cannot_cancel_reg)
            main_menu(message, 3)
        else:
            rec_list=ev_list[message.text][0]
            ev_name=message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(btns.backbtn, btns.skipbtn)
            send = bot.send_message(message.chat.id, text=strs.why_are_u_cancel, reply_markup=markup)
            bot.register_next_step_handler(send, cancel_reg_step_3, rec_list, ev_name)
    else:
        send = bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
        bot.register_next_step_handler(message, cancel_reg_step_2, ev_list)


def cancel_reg_step_3(message, rec_list, ev_name):
    if message.text==btns.backbtn.text:
        main_menu(message, 0)
    else:
        cancel_reason=str(message.text)
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btns.no_chanhced, btns.yes_cancel)
        send=bot.send_message(message.chat.id, text=strs.cancel_last_check+ev_name+'?', reply_markup=markup)
        bot.register_next_step_handler(send, cancel_reg_step_4, rec_list, ev_name, cancel_reason)


def cancel_reg_step_4(message, rec_list, ev_name, cancel_reason):
    if message.text==btns.yes_cancel.text:
        write_in_log(message, 'отменил ' + ev_name + strs.sliv_reason + cancel_reason)
        if ER_DB.del_registration(rec_list):
            bot.send_message(message.chat.id, text=strs.sorry_for_cancel+ev_name)
            send_julia(str='@'+message.from_user.username+strs.sliva+ev_name+strs.sliv_reason+cancel_reason)
        main_menu(message, 3)
    elif message.text==btns.no_chanhced.text:
            bot.send_message(message.chat.id, text=strs.god_bless_u)
            main_menu(message, 0)

    else:
        send=bot.send_message(message.chat.id, text=strs.didnt_get_it, reply_markup=btns.skip_all_handlers)
        bot.register_next_step_handler(message, cancel_reg_step_4, rec_list, ev_name)

def askq_step_1(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btns.backbtn, btns.sendq)
    send = bot.send_message(message.chat.id, text=strs.for_question_text, reply_markup=markup)
    bot.register_next_step_handler(send, askq_step_2)

def askq_step_2(message):
    nick = str(message.from_user.username)
    bot.send_message(julia_chat_id, text=strs.they_wrote_us)
    bot.forward_message(julia_chat_id, message.chat.id, message.id)
    write_in_log(message, log_text=' Написал нам: '+str(message.text))
    bot.send_message(message.chat.id, text=strs.thx)
    main_menu(message, 3)

def clear_handler_by_timeout(message):
    print('timeout started')
    time_out[message.chat.id] = 1
    time.sleep(response_timeout)
    if time_out[message.chat.id]==1:
        print('timeout kick')
        main_menu(message, 2)
    else:
        print('no need timout kick')

def write_in_log(message, log_text):
    if type(log_text)!=str:
        log_text='UNKNOWN MESSAGE'
    current_time = datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
    try:
        nick=message.from_user.username
    except:
        nick='None'
    log_text=current_time+': '+str(nick)+' '+log_text+'\n'
    f = open('log.txt', 'a', encoding='utf-8')
    f.write(log_text)
    f.close()
    print(log_text)

@bot.message_handler(commands=["start"])
def Start(message):
    main_menu(message, 1)
    ER_DB.add_new_user(message.from_user.username, message.chat.id)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    # юзерские функции
    if message.text == btns.myregistrationbtn.text:
        check_registration(message)
    elif message.text == btns.regoneventbtn.text:
        registration_step_1(message)
    elif message.text == btns.sendfeedbackbtn.text:
        feedback_step_1(message)
    elif message.text == btns.allaoboutsubscriptionbtn.text:
        bot.forward_message(message.chat.id, from_chat_id=julia_chat_id, message_id=all_about_sub_message_id)
    elif message.text == btns.paybtn.text:
        bot.send_message(message.chat.id, text=strs.payment_text_info, disable_web_page_preview=True,
                         parse_mode='Markdown')
        #bot.forward_message(message.chat.id, shkoterman_chat_id, payment_message_id)
    elif message.text == btns.pingbtn.text:
        bot.send_message(message.chat.id, text=btns.pingbtn.text)
    elif message.text == btns.cancel.text:
        cancel_reg_step_1(message)
    elif message.text == btns.askqbtn.text:
        askq_step_1(message)


    # админские функции
    elif message.text == btns.sendreminderbtn.text and message.from_user.username in ER_DB.get_admin_list():
        send_reminder_step_1(message)
    elif message.text == btns.askfeedbackbtn.text and message.from_user.username in ER_DB.get_admin_list():
        send_feedback_request_step_1(message)

    # сугубо мои
    elif message.text == btns.testbtn.text and message.chat.id == shkoterman_chat_id:
        print(ER_DB.get_admin_list())
    else:
        main_menu(message, 0)

write_in_log(None, 'bot  hase been started')
bot.infinity_polling(timeout=600, long_polling_timeout=15)
