from telebot import types

### MAIN MENU
### user's
myregistrationbtn = types.KeyboardButton("Мои регистрации")
regoneventbtn = types.KeyboardButton('Зарегистрироваться на мероприятие')
allaoboutsubscriptionbtn = types.KeyboardButton('Все про подписку')
sendfeedbackbtn = types.KeyboardButton('Отзыв о событии')
paybtn = types.KeyboardButton('Оплата')
### admins's
sendreminderbtn = types.KeyboardButton("Отправить напоминание")
askfeedbackbtn = types.KeyboardButton('Разослать запрос фидбэка')
### my
pingbtn = types.KeyboardButton('🖕')
testbtn = types.KeyboardButton("test")

user_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
admin_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
my_main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
user_main_menu_markup.add(myregistrationbtn, regoneventbtn, sendfeedbackbtn, allaoboutsubscriptionbtn, paybtn)
admin_main_menu_markup=user_main_menu_markup.add(sendreminderbtn, askfeedbackbtn)
my_main_menu_markup=admin_main_menu_markup.add(pingbtn, testbtn)





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