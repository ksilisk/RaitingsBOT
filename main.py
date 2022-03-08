from telebot import types
import telebot
import sqlite3
import SQLLib as sql

token = "973541236:AAFLvoGUV1btTIYuoJ8i4NxXv2K4gGrQiBY"
bot = telebot.TeleBot(token)

#read = 525875863


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton('Парень'),
               types.KeyboardButton('Девушка'))
    if sql.check_user(message.chat.id):
        sql.set_position(message.chat.id, 'пол')
    else:
        sql.add_user(message.chat.id, 'пол')
    bot.send_message(message.chat.id, "Вы парень или девушка?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if '_' in call.data:
        data = call.data.split('_')
        if data[0] == 'complaint':
            sql.add_complaint(call.from_user.id)
        elif data[0] == 'my':
            my_photos(call.from_user.id)
        else:
            sql.add_rait(data[1], call.from_user.id, data[0])
            send_photo(call.from_user.id)
    else:
        bot.send_message(call.from_user.id, 'Ошибка! Попробуйте снова!')


@bot.message_handler(content_types=['text'])
def message_hand(message):
    if sql.get_position(message.chat.id) == 'пол':
        man_woman(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'job_choice':
        job_choice(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'who_to':
        who_to_rate(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'rait_or_add_photo':
        rait_or_add_photo(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'whom_to':
        whom_to_rate(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'wait_new_photo':
        if message.text == 'Оценить кого-то':
            send_photo(message.chat.id)
        elif message.text == 'Мои фотографии':
            my_photos(message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение!')
    elif sql.get_position(message.chat.id) == 'wait_rait_photo':
        wait_rait_photo(message.chat.id, message.text)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение!')


@bot.message_handler(content_types=['photo'])
def photos_hand(message):
    if sql.get_position(message.chat.id) == 'add_photo':
        add_photo(message.chat.id, message.photo[len(message.photo) - 1])
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение!')


def man_woman(user_id, text):
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton('Парень'),
               types.KeyboardButton('Девушка'))
    if text in ['Парень', 'Девушка']:
        if text == 'Парень':
            sql.set_gender(user_id, 'man')
        else:
            sql.set_gender(user_id, 'woman')
        markup = types.ReplyKeyboardMarkup()
        markup.row(types.KeyboardButton('Хочу пока оценивать других!'),
                   types.KeyboardButton('Хочу, чтобы оценили меня!'))
        bot.send_message(user_id, 'Отлично!\nТеперь ответьте как хотите продолжить?', reply_markup=markup)
        sql.set_position(user_id, 'job_choice')
    else:
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def job_choice(user_id, text):
    markup = types.ReplyKeyboardMarkup()
    if text == 'Хочу, чтобы оценили меня!':
        markup.row(types.KeyboardButton('Всем'),
                   types.KeyboardButton('Парням'),
                   types.KeyboardButton('Девушкам'))
        bot.send_message(user_id, 'Кому показывать твои фотографии?', reply_markup=markup)
        sql.set_position(user_id, 'who_to')
    elif text == 'Хочу пока оценивать других!':
        markup.row(types.KeyboardButton('Всех'),
                   types.KeyboardButton('Парней'),
                   types.KeyboardButton('Девушек'))
        bot.send_message(user_id, 'Кого ты хочешь оценивать?', reply_markup=markup)
        sql.set_position(user_id, 'whom_to')
    else:
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!')


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
        markup.row(types.KeyboardButton('Всем'),
                   types.KeyboardButton('Парнем'),
                   types.KeyboardButton('Девушкам'))
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def add_photo(user_id, photo):
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton('Добавить еще фото!'),
               types.KeyboardButton('Оценить кого-то!'))
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
    else:
        markup = types.ReplyKeyboardMarkup()
        markup.row(types.KeyboardButton('Всех'),
                   types.KeyboardButton('Парней'),
                   types.KeyboardButton('Девушек'))
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def send_photo(user_id): # есть баг, надо пофиксить
    if sql.search_photo(user_id) != 0:
        photo_id = str(sql.search_photo(user_id)[1])
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton('1', callback_data=('1_' + photo_id)),
                   types.InlineKeyboardButton('2', callback_data=('2_' + photo_id)),
                   types.InlineKeyboardButton('3', callback_data=('3_' + photo_id)),
                   types.InlineKeyboardButton('4', callback_data=('4_' + photo_id)),
                   types.InlineKeyboardButton('5', callback_data=('5_' + photo_id)),
                   types.InlineKeyboardButton('6', callback_data=('6_' + photo_id)),
                   types.InlineKeyboardButton('7', callback_data=('7_' + photo_id)),
                   types.InlineKeyboardButton('8', callback_data=('8_' + photo_id)),
                   types.InlineKeyboardButton('9', callback_data=('9_' + photo_id)),
                   types.InlineKeyboardButton('10', callback_data=('10_' + photo_id)),
                   types.InlineKeyboardButton('Жалоба', callback_data=('complaint_' + photo_id)),
                   types.InlineKeyboardButton('Мои фото', callback_data='my_photo'))
        file_id = str(sql.search_photo(user_id)[0])
        bot.send_photo(user_id, file_id, reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup()
        markup.row(types.KeyboardButton('Оценить кого-то'),
                   types.KeyboardButton('Мои фотографии'))
        bot.send_message(user_id, 'На данный момент новых фотографий нет! Попробуйте позже!', reply_markup=markup)
        sql.set_position(user_id, 'wait_new_photo')


def my_photos(user_id):
    data = sql.my_photos_raitings(user_id)
    if data == {}:
        markup = types.ReplyKeyboardMarkup()
        markup.row(types.KeyboardButton('Продолжить оценивать!'),
                   types.KeyboardButton('Добавить фото!'))
        sql.set_position(user_id, 'rait_or_add_photo')
        bot.send_message(user_id, 'У Вас нет фотографий, которые могли бы оценивать другие пользователи!', reply_markup=markup)
    else:
        for key, value in data.items():
            bot.send_photo(user_id, sql.get_file_id(key), caption='Среднее всех оценок: ' + str(value))
        markup = types.ReplyKeyboardMarkup()
        markup.row(types.KeyboardButton('Оценить кого-то!'),
                   types.KeyboardButton('Добавить еще фото!'))
        bot.send_message(user_id, 'Что дальше?)', reply_markup=markup)
        sql.set_position(user_id, 'wait_rait_photo')


def wait_rait_photo(user_id, text):
    if text == 'Добавить еще фото!':
        sql.set_position(user_id, 'add_photo')
        bot.send_message(user_id, 'Пришлите фото!')
    elif text == 'Оценить кого-то!':
        if sql.get_whom_to(user_id) == 'None':
            markup = types.ReplyKeyboardMarkup()
            markup.row(types.KeyboardButton('Всех'),
                       types.KeyboardButton('Парней'),
                       types.KeyboardButton('Девушек'))
            bot.send_message(user_id, 'Кого ты хочешь оценивать?', reply_markup=markup)
            sql.set_position(user_id, 'whom_to')
        else:
            send_photo(user_id)
    else:
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!')


def rait_or_add_photo(user_id, text):
    if text == 'Продолжить оценивать!':
        send_photo(user_id)
    elif text == 'Добавить фото!':
        if sql.get_who_to(user_id) == 'None':
            markup = types.ReplyKeyboardMarkup()
            markup.row(types.KeyboardButton('Всем'),
                       types.KeyboardButton('Парням'),
                       types.KeyboardButton('Девушкам'))
            bot.send_message(user_id, 'Кому показывать твои фотографии?', reply_markup=markup)
            sql.set_position(user_id, 'who_to')
        else:
            sql.set_position(user_id, 'add_photo')
            bot.send_message(user_id, 'Пришлите фото!')
    else:
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!')


bot.infinity_polling()
