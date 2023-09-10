import telebot
import telegram
from telebot import types
bot = telebot.TeleBot('5806434689:AAG383Pr1XxSpl4vjJ9rNFR27xJJA19bs0g') # this is prod
@bot.message_handler(commands=["start"])                                    #я не знаю что это(((( видимо штука которая ждёт сообщения, я хз
def Start(m):
    bot.send_message(m.from_user.id,
                     text="Привет, я пока временно не работаю, меня уже чинят. А пока для регистрации переходи в [форму](https://airtable.com/shreKeGjNLsXnQAe5)",
                     disable_web_page_preview=True, parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=["text"])  # я не знаю что это(((( видимо штука которая ждёт сообщения, я хз
def handle_text(message):
    bot.send_message(message.from_user.id,
                     text="Привет, я пока временно не работаю, меня уже чинят. А пока для регистрации переходи в [форму](https://airtable.com/shreKeGjNLsXnQAe5)" , disable_web_page_preview=True, parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

bot.polling(none_stop=True, interval=0)