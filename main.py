from telebot import types
import telebot
import sqlite3
import SQLLib as sql

token = "973541236:AAFLvoGUV1btTIYuoJ8i4NxXv2K4gGrQiBY"
bot = telebot.TeleBot(token)


# print(sql.aaaa(11))
# print(sql.is_photo_raited(12))
# print(sql.search_photo(12))#sql.add_new_photo(12, '5576567567856')


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
            sql.set_position(message.chat.id, 'add_photo')
            bot.send_message(message.chat.id, 'Пришлите фото!')
        elif message.text == 'Оценить кого-то!':
            if sql.get_whom_to(message.chat.id) == 'None':
                markup = types.ReplyKeyboardMarkup()
                button_all = types.KeyboardButton('Всех')
                button_man = types.KeyboardButton('Парней')
                button_woman = types.KeyboardButton('Девушек')
                markup.row(button_man, button_woman, button_all)
                bot.send_message(message.chat.id, 'Кого ты хочешь оценивать?', reply_markup=markup)
                sql.set_position(message.chat.id, 'whom_to')
            else:
                send_photo(message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение!')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение!')


@bot.message_handler(content_types=['photo'])
def photos_hand(message):
    if sql.get_position(message.chat.id) == 'add_photo':
        add_photo(message.chat.id, message.photo[len(message.photo) - 1])


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


def who_to_rate(user_id, text):  # кому показывать фото для оценки
    if text in ['Всем', 'Парням', 'Девушкам']:
        if text == 'Всем':
            sql.set_who_to(user_id, 'all')
        elif text == 'Парням':
            sql.set_who_to(user_id, 'man')
        elif text == 'Девушкам':
            sql.set_who_to(user_id, 'woman')
        bot.send_message(user_id, 'Отлично!\nТеперь пришли фотографию, которую будут оценивать другие пользователи!')
        sql.set_position(user_id, 'add_photo')
    else:
        markup = types.ReplyKeyboardMarkup()
        button_all = types.KeyboardButton('Всем')
        button_man = types.KeyboardButton('Парнем')
        button_woman = types.KeyboardButton('Девушкам')
        markup.row(button_all, button_man, button_woman)
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def add_photo(user_id, photo):
    markup = types.ReplyKeyboardMarkup()
    button_new_photo = types.KeyboardButton('Добавить еще фото!')
    button_rait_anyone = types.KeyboardButton('Оценить кого-то!')
    markup.row(button_new_photo, button_rait_anyone)
    bot.send_message(user_id,
                     'Отлично!\nФотография добавлена!\nКак только кто-то ее оценит, я отправлю Вам уведомление!',
                     reply_markup=markup)
    sql.add_new_photo(user_id, photo.file_id)
    sql.set_position(user_id, 'wait_rait_photo')


def whom_to_rate(user_id, text):  # кого показывать для оценки
    if text in ['Всех', 'Парней', 'Девушек']:
        if text == 'Всех':
            sql.set_whom_to(user_id, 'all')
        elif text == 'Парней':
            sql.set_whom_to(user_id, 'man')
        elif text == 'Девушек':
            sql.set_whom_to(user_id, 'woman')
        send_photo(user_id)
        # дописать
    else:
        markup = types.ReplyKeyboardMarkup()
        button_all = types.KeyboardButton('Всех')
        button_man = types.KeyboardButton('Парней')
        button_woman = types.KeyboardButton('Девушек')
        markup.row(button_all, button_man, button_woman)
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def send_photo(user_id):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('1', callback_data='1')
    button2 = types.InlineKeyboardButton('2', callback_data='2')
    button3 = types.InlineKeyboardButton('3', callback_data='3')
    button4 = types.InlineKeyboardButton('4', callback_data='4')
    button5 = types.InlineKeyboardButton('5', callback_data='5')
    button6 = types.InlineKeyboardButton('6', callback_data='6')
    button7 = types.InlineKeyboardButton('7', callback_data='7')
    button8 = types.InlineKeyboardButton('8', callback_data='8')
    button9 = types.InlineKeyboardButton('9', callback_data='9')
    button10 = types.InlineKeyboardButton('10', callback_data='10')
    buttonСomplaint = types.InlineKeyboardButton('Жалоба', callback_data='complaint')
    buttonMy = types.InlineKeyboardButton('Мои фото', callback_data='my_photo')
    markup.row(button1,button2,button3,button4,button5,button6,button7,button8,button9,button10,buttonСomplaint,buttonMy)
    file_id = sql.search_photo(user_id)
    if file_id == 0:
        bot.send_message(user_id, '')
    bot.send_photo(user_id, file_id, reply_markup=markup)



bot.infinity_polling()
