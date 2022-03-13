from telebot import types
import telebot
import sqlite3
import SQLLib as sql

token = "973541236:AAFLvoGUV1btTIYuoJ8i4NxXv2K4gGrQiBY"
bot = telebot.TeleBot(token)

# read = 525875863
markup_who_to = types.ReplyKeyboardMarkup(True, True).row(types.KeyboardButton('Всем'),
                                                          types.KeyboardButton('Парнем'),
                                                          types.KeyboardButton('Девушкам'))

markup_whom_to = types.ReplyKeyboardMarkup(True, True).row(types.KeyboardButton('Всех'),
                                                           types.KeyboardButton('Парней'),
                                                           types.KeyboardButton('Девушек'))


@bot.message_handler(commands=['start'], func=lambda message: not sql.check_ban(message.chat.id))
def start(message):
    markup = types.ReplyKeyboardMarkup(True, True)
    markup.row(types.KeyboardButton('Парень'),
               types.KeyboardButton('Девушка'))
    if sql.check_user(message.chat.id):
        pos = sql.get_position(message.chat.id)
        if pos.split('_')[0] == 'start':
            if int(pos.split('_')[1]) >= 5:
                sql.ban_user(message.chat.id)
                bot.send_message(message.chat.id, 'Вы были забанены за DDOS')
            else:
                sql.set_position(message.chat.id, 'start_' + str(int(pos.split('_')[1])+1))
        else:
            sql.set_position(message.chat.id, 'start_1')
    else:
        sql.add_user(message.chat.id, 'start_1')
    bot.send_message(message.chat.id, "Вы парень или девушка?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: not sql.check_ban(call.from_user.id))
def callback_query(call):
    if '_' in call.data:
        data = call.data.split('_')
        if data[0] == 'complaint':
            sql.add_complaint(sql.get_photo_owner(data[1]))
            if int(sql.get_complants(sql.get_photo_owner(data[1]))) >= 5:
                bot.send_message(sql.get_photo_owner(data[1]), 'Вы были забанены за большое количество жалоб!')
                sql.ban_user(sql.get_photo_owner(data[1]))
            sql.add_rait(data[1], call.from_user.id, data[0])
            send_photo(call.from_user.id)
        elif data[0] == 'my':
            my_photos(call.from_user.id)
        elif data[0] == 'del':
            sql.del_photo(data[1])
        else:
            sql.add_rait(data[1], call.from_user.id, data[0])
            send_photo(call.from_user.id)
            bot.send_photo(sql.get_photo_owner(data[1]),
                           sql.get_file_id(data[1]),
                           caption=('Вашу фотографию оценили на: ' + data[0]))
    else:
        bot.send_message(call.from_user.id, 'Ошибка! Попробуйте снова!')


@bot.message_handler(content_types=['text'], func=lambda message: not sql.check_ban(message.chat.id))
def message_hand(message):
    if sql.get_position(message.chat.id).split('_')[0] == 'start':
        man_woman(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'job_choice':
        job_choice(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'who_to':
        who_to_rate(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'rait_or_add_photo':
        rait_or_add_photo(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'whom_to':
        whom_to_rate(message.chat.id, message.text)
    elif sql.get_position(message.chat.id) == 'banned':
        pass
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


@bot.message_handler(content_types=['photo'], func=lambda message: not sql.check_ban(message.chat.id))
def photos_hand(message):
    if sql.get_position(message.chat.id) == 'add_photo':
        add_photo(message.chat.id, message.photo[len(message.photo) - 1])
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение!')


def man_woman(user_id, text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton('Парень'),
               types.KeyboardButton('Девушка'))
    if text in ['Парень', 'Девушка']:
        if text == 'Парень':
            sql.set_gender(user_id, 'man')
        else:
            sql.set_gender(user_id, 'woman')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton('Хочу пока оценивать других!'),
                   types.KeyboardButton('Хочу, чтобы оценили меня!'))
        bot.send_message(user_id, 'Отлично!\nТеперь ответьте как хотите продолжить?', reply_markup=markup)
        sql.set_position(user_id, 'job_choice')
    else:
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup)


def job_choice(user_id, text):
    if text == 'Хочу, чтобы оценили меня!':
        bot.send_message(user_id, 'Кому показывать твои фотографии?', reply_markup=markup_who_to)
        sql.set_position(user_id, 'who_to')
    elif text == 'Хочу пока оценивать других!':
        bot.send_message(user_id, 'Кого ты хочешь оценивать?', reply_markup=markup_whom_to)
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
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup_who_to)


def add_photo(user_id, photo):
    markup = types.ReplyKeyboardMarkup(True, True)
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
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!', reply_markup=markup_whom_to)


def send_photo(user_id):  # есть баг, надо пофиксить
    if sql.search_photo(user_id) != 0:
        photo_id = str(sql.search_photo(user_id)[1])
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.row(types.InlineKeyboardButton('1', callback_data=('1_' + photo_id)),
                   types.InlineKeyboardButton('2', callback_data=('2_' + photo_id)),
                   types.InlineKeyboardButton('3', callback_data=('3_' + photo_id)),
                   types.InlineKeyboardButton('4', callback_data=('4_' + photo_id)),
                   types.InlineKeyboardButton('5', callback_data=('5_' + photo_id)))
        markup.row(types.InlineKeyboardButton('6', callback_data=('6_' + photo_id)),
                   types.InlineKeyboardButton('7', callback_data=('7_' + photo_id)),
                   types.InlineKeyboardButton('8', callback_data=('8_' + photo_id)),
                   types.InlineKeyboardButton('9', callback_data=('9_' + photo_id)),
                   types.InlineKeyboardButton('10', callback_data=('10_' + photo_id)))
        markup.row(types.InlineKeyboardButton('Жалоба', callback_data=('complaint_' + photo_id)),
                   types.InlineKeyboardButton('Мои фото', callback_data='my_photo'))
        file_id = str(sql.search_photo(user_id)[0])
        bot.send_photo(user_id, file_id, reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(True, True)
        markup.row(types.KeyboardButton('Оценить кого-то'),
                   types.KeyboardButton('Мои фотографии'))
        bot.send_message(user_id, 'На данный момент новых фотографий нет! Попробуйте позже!', reply_markup=markup)
        sql.set_position(user_id, 'wait_new_photo')


def my_photos(user_id):
    data = sql.my_photos_raitings(user_id)
    if data == {}:
        markup = types.ReplyKeyboardMarkup(True, True)
        markup.row(types.KeyboardButton('Продолжить оценивать!'),
                   types.KeyboardButton('Добавить фото!'))
        sql.set_position(user_id, 'rait_or_add_photo')
        bot.send_message(user_id, 'У Вас нет фотографий, которые могли бы оценивать другие пользователи!',
                         reply_markup=markup)
    else:
        for key, value in data.items():
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton('Удалить!', callback_data=('del_' + str(key))))
            bot.send_photo(user_id, sql.get_file_id(key), caption='Среднее всех оценок: ' + str(value),
                           reply_markup=markup)
        markup = types.ReplyKeyboardMarkup(True, True)
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
            bot.send_message(user_id, 'Кого ты хочешь оценивать?', reply_markup=markup_whom_to)
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
            bot.send_message(user_id, 'Кому показывать твои фотографии?', reply_markup=markup_who_to)
            sql.set_position(user_id, 'who_to')
        else:
            sql.set_position(user_id, 'add_photo')
            bot.send_message(user_id, 'Пришлите фото!')
    else:
        bot.send_message(user_id, 'Пожалуйста, введите корректное значение!')


users = sql.get_all_users()
for i in range(len(users)):
    bot.send_message(users[i][0], 'Бот был перезапущен, попробуйте команду снова!')
bot.infinity_polling(skip_pending=True)