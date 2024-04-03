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

### admins's
sendreminderbtn = types.KeyboardButton("Отправить напоминание")
askfeedbackbtn = types.KeyboardButton('Разослать запрос фидбэка')
### my

pingbtn = types.KeyboardButton('🖕')
testbtn = types.KeyboardButton("test")
send_all_btn = types.KeyboardButton("send to all")

user_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
admin_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
my_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
user_main_menu_markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel, askqbtn, olivebtn)
admin_main_menu_markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel, askqbtn, olivebtn, sendreminderbtn, askfeedbackbtn)
my_main_menu_markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel, askqbtn, olivebtn, sendreminderbtn, askfeedbackbtn, pingbtn, testbtn, send_all_btn)

skip_all_handlers = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Главное меню', callback_data='05'))



changenamebtn = types.KeyboardButton('Изменить имя')
changenickbtn = types.KeyboardButton('Изменить ник')
backbtn = types.KeyboardButton("Отмена")
mainmenubtn = types.KeyboardButton("Главное меню")
yesbtn = types.KeyboardButton('Да')
nobtn = types.KeyboardButton('Нет')
plusonebtn = types.KeyboardButton('Меня +1')
minusonebtn = types.KeyboardButton('Только меня')
readybtn = types.KeyboardButton('Готово')
skipbtn = types.KeyboardButton('Пропустить')
yes_cancel = types.KeyboardButton('Да, отменить регистрацию')
no_chanhced = types.KeyboardButton('Нет, я передумал_а, не отменять')

olive_got_it1 = types.KeyboardButton('Понятно, что дальше')
olive_got_it2 = types.KeyboardButton('Окей, а как делать-то?')
olive_got_it3 = types.KeyboardButton('Понятно, пойду в магазин')
olive_didnt_get_it = types.KeyboardButton('Всё неправильно, сейчас напишу, что именно')
