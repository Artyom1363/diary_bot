# -*- coding: utf-8 -*-
import config
import telebot
import random
from telebot import types
import diary
import sqlite3
import datetime
import sys
sys.path.insert(0, 'cal')
import telebot_calendar
from telebot_calendar import CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery

calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")

bot = telebot.TeleBot(config.token)
output = open('log.txt', 'a')

#phys_bmstu
#bot.send_message(556001234, "yes this is text")
#1130614305
'''bot.send_message(556001234, 'Привет, пожалуйста, если '
	'возникли какие-то проблемы, пожалуйста напиши мне: '
	'@htppkt')
bot.send_message(556001234, 'сообщение ушло')'''


@bot.message_handler(commands=["cal"])
def show_calendar(message):
    """
    Catches a message with the command "start" and sends the calendar

    :param message:
    :return:
    """
    if (type(message) == str):
    	user_id = message
    else:
    	user_id = message.chat.id
    now = datetime.datetime.now()  # Get the current date
    bot.send_message(
       	user_id,
        "Укажите дату занятия",
        reply_markup=telebot_calendar.create_calendar(
            name=calendar_1.prefix,
            year=now.year,
            month=now.month,  # Specify the NAME of your calendar
        ),
    )

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton('Сгенерировать дневник')
item2 = types.KeyboardButton('Сформировать свою тренировку')


def print_menu(user_id):
	bot.send_message(user_id, 'Вы находитесь в меню, нажмите:\n'
		'\n● /diary чтобы сгенерировать дневник'
		'\n● /workout чтобы написать собственную тренировку'
		'\n● /del чтобы удалить все данные о себе',
		reply_markup = markup)



def print_make_diary(user_id):
	content = ('Чтобы сгенерировать дневник'
		' вам необходимо указать какую вы будете'
		' использовать тренировку\n'
		'\n● /auto автоматически сгенирированная')
	workouts = diary.show_workouts(user_id)
	if workouts == '0':
		pass
	else:
		content += workouts
	content += '\n● /menu чтобы вернуться в меню'
	bot.send_message(user_id, content, reply_markup = markup)



def print_get_add(user_id):
	bot.send_message(user_id, 'Вы успешно добавили тренировку, '
		'нажмите:'
		'\n● /get чтобы скачать дневник'
		'\n● /more чтобы добавить еще тренировки в дневник',
		reply_markup = markup)



@bot.message_handler(commands=['start'])
def welcome(message):
	user_id = message.chat.id
	diary.print_f(user_id, message.text)
	if diary.init(user_id) == '1':
		bot.send_message(user_id, 'Вы уже зарегистрированы')
		return
	bot.send_message(user_id, 'Привет, я бот, который может '
					'создать за тебя дневник самоподготовки')
	bot.send_message(user_id, 'Напиши свое ФИО')



@bot.message_handler(content_types=["text"])
def main_func(message, ident = None):
	if (type(message) == str):
		user_id = str(ident);
		content = message
	else:
		user_id = str(message.chat.id)
		content = message.text

	diary.print_f(user_id, content)

	state = diary.get_state(user_id)
	
	#delete
	if content == '/del':
		diary.delete_me(user_id)
		bot.send_message(user_id, 'Нажмите /start чтобы зарегистрироваться')
		return

	#если новый пользователь
	if state == 'no_such_user':
		diary.init(user_id)
		bot.send_message(user_id, 'Привет, я бот, который может '
					'создать за тебя дневник самоподготовки')
		bot.send_message(user_id, 'Напиши свое ФИО')
		return

	#состояние заполнения персональных данных
	if state == 'obtaining_personal_data':
		content = diary.change_state(user_id, content)
		if content == 'end':
			print_menu(user_id)
			return
		bot.send_message(user_id, content)

	#if user is in menu
	elif state == 'menu':
		diary.change_state(user_id, content)
		state = diary.get_state(user_id)
		if state == 'make_diary':
			print_make_diary(user_id)
		elif state == 'make_workout':
			content = diary.generation_your_own_workout(user_id, content)
			bot.send_message(user_id, content)
		else:
			bot.send_message(user_id, 'Произошла ошибка, '
				'попробуйте еще раз', reply_markup = markup)
			print_menu(user_id)

	#if user clicked '/diary'
	elif state == 'make_diary':
		code = diary.change_state(user_id, content)
		if code != '0':
			bot.send_message(user_id, 'Произошла ошибка, '
				'попробуйте еще раз', reply_markup = markup)
			print_make_diary(user_id)
			return
		if content == '/menu':
			print_menu(user_id)
			return
		else:
			show_calendar(user_id)

	#selectint_workout_day
	elif state == 'swd':
		code = diary.change_state(user_id, content)
		if code != '0':
			bot.send_message(user_id, 'Произошла ошибка, '
				'попробуйте еще раз', reply_markup = markup)
			show_calendar(user_id)
			return
		print_get_add(user_id)

	#user can get diary or append workout
	elif state == 'get_add':
		code = diary.change_state(user_id, content)
		if code != '0':
			bot.send_message(user_id, 'Произошла ошибка, '
				'попробуйте еще раз', reply_markup = markup)
			print_get_add(user_id)

		if content == '/get':
			diary.gen_diary_txt(user_id)
			f = open("res_diary.docx", 'rb');
			bot.send_document(user_id, f)
			print_menu(user_id)

		elif content == '/more':
			if diary.get_quantity_of_dates(user_id) >= 7:
				bot.send_message(user_id, 'Вы ввели максимально '
							'возможное кол-во дат, вот ваш дневник')
				diary.gen_diary_txt(user_id)
				f = open("res_diary.docx", 'rb');
				bot.send_document(user_id, f)
				print_menu(user_id)
				return
			print_make_diary(user_id)


	#состояние генерации собственной тренировки
	elif (state == 'generating_own_training' or content == '/gen'):
		content = diary.generation_your_own_workout(user_id, content)
		if content == 'end':
			print_menu(user_id)
			return
		bot.send_message(user_id, content)

	else:
		diary.print_f("ERROR: ", user_id, " ", content)
		#del students_db[str(message.chat.id)]
		bot.send_message(user_id, 'Простите, что-то пошло не так')
		

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """

    # At this point, we are sure that this calendar is ours. 
    #So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar_1.sep)
    # Processing the calendar. Get either the date or 
    #None if the buttons are of a different type
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, 
        year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is 
    # selected, you can execute your code. I sent a message.
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=str(date.strftime('%d.%m.%Y')),
            reply_markup=ReplyKeyboardRemove(),
        )
        #diary.print_f(call.from_user.id, date.strftime('%d.%m.%Y'))
        main_func(date.strftime('%d.%m.%Y'), call.from_user.id)

    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Cancellation",
            reply_markup=ReplyKeyboardRemove(),
        )
        diary.print_f(call.from_user.id, 'cancel')


if __name__ == '__main__':
    bot.infinity_polling()
