from telebot import types
import telebot
import sqlite3
import SQLLib as sql

token = "973541236:AAFLvoGUV1btTIYuoJ8i4NxXv2K4gGrQiBY"
bot = telebot.TeleBot(token)

#print(sql.aaaa(11))
#print(sql.is_photo_raited(12))
print(sql.search_photo(12))#sql.add_new_photo(12, '5576567567856')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    button_man = types.KeyboardButton('Парень')
    button_woman = types.KeyboardButton('Девушка')
    markup.row(button_man, button_woman)
    if sql.check_user(message.chat.id):
        sql.set_position(message.chat.id, 'пол')
    else:
        sql.add_user(message.chat.id, 'пол')
    bot.send_message(message.chat.id, "Вы парень или девушка?", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def message_hand(message):
    if sql.get_position(message.chat.id) == 'пол':
        man_woman(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'job_choice':
        job_choice(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'who_to':
        who_to_rate(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'whom_to':
        whom_to_rate(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'wait_rait_photo':
        if message.text == 'Добавить еще фото!':
            sql.set_position(message.chat.id, 'send_photo')
            bot.send_message(message.chat.id, 'Пришлите фото!')
        elif message.text == 'Оценить кого-то!':
            sql.get_position(message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение!')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение!')



@bot.message_handler(content_types=['photo'])
def photos_hand(message):
    if sql.get_position(message.chat.id) == 'send_photo':
        send_photo(message.chat.id, message.photo[len(message.photo) - 1])


def man_woman(user_id, text):
    markup = types.ReplyKeyboardMarkup()
    button_man = types.KeyboardButton('Парень')
    button_woman = types.KeyboardButton('Девушка')
    markup.row(button_man, button_woman)
    if text in ['Парень', 'Девушка']:
        markup = types.ReplyKeyboardMarkup()
        button1 = types.KeyboardButton('Хочу пока оценивать других!')
        button2 = types.KeyboardButton('Хочу, чтобы оценили меня!')
        markup.row(button1, button2)
        sql.set_gender(user_id, text)
        bot.send_message(user_id, 'Отлично!\nТеперь ответьте как хотите продолжить?', reply_markup=markup)
        sql.set_position(user_id, 'job_choice')
    else:
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def job_choice(user_id, text):
    markup = types.ReplyKeyboardMarkup()
    if text == 'Хочу, чтобы оценили меня!':
        button_all = types.KeyboardButton('Всем')
        button_man = types.KeyboardButton('Парням')
        button_woman = types.KeyboardButton('Девушкам')
        markup.row(button_man, button_woman, button_all)
        bot.send_message(user_id, 'Кому показывать твои фотографии?', reply_markup=markup)
        sql.set_position(user_id, 'who_to')
    elif text == 'Хочу пока оценивать других!':
        button_all = types.KeyboardButton('Всех')
        button_man = types.KeyboardButton('Парней')
        button_woman = types.KeyboardButton('Девушек')
        markup.row(button_man, button_woman, button_all)
        bot.send_message(user_id, 'Кого ты хочешь оценивать?', reply_markup=markup)
        sql.set_position(user_id, 'whom_to')
    else:
        button1 = types.KeyboardButton('Хочу пока оценивать других!')
        button2 = types.KeyboardButton('Хочу, чтобы оценили меня!')
        markup.row(button1, button2)
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def who_to_rate(user_id, text):
    if text in ['Всем', 'Парням', 'Девушкам']:
        if text == 'Всем':
            sql.set_who_to(user_id, 'all')
        elif text == 'Парням':
            sql.set_who_to(user_id, 'man')
        elif text == 'Девушкам':
            sql.set_who_to(user_id, 'woman')
        bot.send_message(user_id, 'Отлично!\nТеперь пришли фотографию, которую будут оценивать другие пользователи!')
        sql.set_position(user_id, 'send_photo')
    else:
        markup = types.ReplyKeyboardMarkup()
        button_all = types.KeyboardButton('Всем')
        button_man = types.KeyboardButton('Парнем')
        button_woman = types.KeyboardButton('Девушкам')
        markup.row(button_all, button_man, button_woman)
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def send_photo(user_id, photo):
    markup = types.ReplyKeyboardMarkup()
    button_new_photo = types.KeyboardButton('Добавить еще фото!')
    button_rait_anyone = types.KeyboardButton('Оценить кого-то!')
    markup.row(button_new_photo, button_rait_anyone)
    bot.send_message(user_id, 'Отлично!\nФотография добавлена!\nКак только кто-то ее оценит, я отправлю Вам уведомление!',
                     reply_markup=markup)
    sql.add_new_photo(user_id, photo.file_id)
    sql.set_position(user_id, 'wait_rait_photo')


def whom_to_rate(user_id, text):
    print()


#    markup = types.ReplyKeyboardMarkup()
#	if text in ['Всех', 'Парней', 'Девушек']:


bot.infinity_polling()