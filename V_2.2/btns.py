from telebot import types

### MAIN MENU
### user's
myregistrationbtn = types.KeyboardButton("Мои регистрации")
regoneventbtn = types.KeyboardButton('Зарегистрироваться на мероприятие')
allaoboutsubscriptionbtn = types.KeyboardButton('Все про подписку')
sendfeedbackbtn = types.KeyboardButton('Отзыв о событии')
paybtn = types.KeyboardButton('Оплата')
cancel = types.KeyboardButton('Отменить регистрацию')

### admins's
sendreminderbtn = types.KeyboardButton("Отправить напоминание")
askfeedbackbtn = types.KeyboardButton('Разослать запрос фидбэка')
### my

pingbtn = types.KeyboardButton('🖕')
testbtn = types.KeyboardButton("test")

user_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
admin_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
my_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
user_main_menu_markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel)
admin_main_menu_markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel, sendreminderbtn, askfeedbackbtn)
my_main_menu_markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn, cancel, sendreminderbtn, askfeedbackbtn, pingbtn, testbtn)





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