from telebot import types

### MAIN MENU
### user's
myregistrationbtn = types.KeyboardButton("Мои регистрации")
regoneventbtn = types.KeyboardButton('Зарегистрироваться на мероприятие')
allaoboutsubscriptionbtn = types.KeyboardButton('ensalada.more')
sendfeedbackbtn = types.KeyboardButton('Отзыв о событии')
paybtn = types.KeyboardButton('Оплата')
cancel = types.KeyboardButton('Отменить регистрацию')
askqbtn = types.KeyboardButton('Написать нам')
sendq = types.KeyboardButton('Отправить')
olivebtn = types.KeyboardButton('Наш рецепт 🥗')
event_calendar = types.KeyboardButton('Календарь мероприятий 🆕')


### admins's
sendreminderbtn = types.KeyboardButton("Отправить напоминание")
askfeedbackbtn = types.KeyboardButton('Разослать запрос фидбэка')
### my

pingbtn = types.KeyboardButton('🖕')
testbtn = types.KeyboardButton("test")
send_all_btn = types.KeyboardButton("send to all")
get_counts = types.KeyboardButton('get_counts')

user_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
admin_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
my_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
user_main_menu_markup.add(myregistrationbtn, regoneventbtn, event_calendar, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel, askqbtn, olivebtn)
admin_main_menu_markup.add(myregistrationbtn, regoneventbtn, event_calendar, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel, askqbtn, olivebtn, sendreminderbtn, askfeedbackbtn)
my_main_menu_markup.add(myregistrationbtn, regoneventbtn, event_calendar, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel, askqbtn, olivebtn, sendreminderbtn, askfeedbackbtn, pingbtn, testbtn, send_all_btn, get_counts)

skip_all_handlers = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Главное меню', callback_data='05'))



changenamebtn = types.KeyboardButton('Изменить имя')
changenickbtn = types.KeyboardButton('Изменить ник')
cancelbtn = types.KeyboardButton("Отмена")
mainmenubtn = types.KeyboardButton("Главное меню")
yesbtn = types.KeyboardButton('Да')
nobtn = types.KeyboardButton('Нет')
plusonebtn = types.KeyboardButton('Меня +1')
minusonebtn = types.KeyboardButton('Только меня')
readybtn = types.KeyboardButton('Готово')
skipbtn = types.KeyboardButton('Пропустить')
yes_cancel = types.KeyboardButton('Да, отменить регистрацию')
no_chanhced = types.KeyboardButton('Нет, я передумал_а, не отменять')
backbtn = types.KeyboardButton('Назад')

olive_got_it1 = types.KeyboardButton('Понятно, что дальше')
olive_got_it2 = types.KeyboardButton('Окей, а как делать-то?')
olive_got_it3 = types.KeyboardButton('Понятно, пойду в магазин')
olive_didnt_get_it = types.KeyboardButton('Всё неправильно, сейчас напишу, что именно')



calendar_btns_event_dict = {
    'food':types.KeyboardButton('🍢Поесть / 🍹Выпить'),
    'movie':types.KeyboardButton('🎞Кино / 🎭Театр / 🎙Стендап'),
    'expo':types.KeyboardButton('🍌Выставки / 🏛Музеи / 🧑‍🏫Лекции'),
    'fest':types.KeyboardButton('🎪Городская культура'),
    'other':types.KeyboardButton('🤷‍♂️Другое')
}

calendar_all = types.KeyboardButton('👆Все')
calendar_ensalada = types.KeyboardButton('🥗Только мероприятия энсалады')

calendar_btns_time_gates_dict={
    'today':types.KeyboardButton('🗓Сегодня'),
    'this_week':types.KeyboardButton('🗓На этой неделе'),
    'next_week':types.KeyboardButton('🗓На следующей неделе'),
    'this_month':types.KeyboardButton('🗓В этом месяце'),
}


calendar_time_gate_today = types.KeyboardButton('Сегодня')
calendar_time_gate_this_week = types.KeyboardButton('На этой неделе')
calendar_time_gate_next_week = types.KeyboardButton('На следующей неделе')
calendar_time_gate_this_month = types.KeyboardButton('В этом месяце')
calendar_time_gate_all = types.KeyboardButton('Все мероприятия')

def go_to_reg_btn(call_data):
    go_to_reg_btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Зарегистрироваться', callback_data=call_data))
    return go_to_reg_btn