# -*- coding: utf-8 -*-
from docxtpl import DocxTemplate
import random
import sqlite3
import datetime
#доработить fill_personal_data


#plan before relise
'''
#добавить календарь
#тестирование с изменным id 
#заливка на сервер
#print в файл
#вынести отдельно проверку даты или тренировки
#переделать проверку даты 
#переделать проверку команды на выбор тренировки
#добавить справку

'''
def print_f(*args):
	output = open('log.txt', 'a')
	now = datetime.datetime.now()
	output.write(str(now))
	output.write(' ')
	for arg in args:
		output.write(str(arg))
		output.write(' ')
	output.write('\n')
	output.close()


def init(ident):
	"""
	инициализация

	"""
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT count() FROM students WHERE user_id = ?""",(ident, ))
		data = cur.fetchall()
		if data[0][0] != 0:
			print_f("try to register sec time ", ident)
			return '1'
		cur.execute("""INSERT INTO students (user_id, name, 
			birth_day, group_, weight, height, 
			state)  VALUES (?, ?, ?, ?, ?, ?, ?) """, 
			(ident, '', '', '', '', '', 'expect_name'))
		return '0'


def select_work(ident, message):
	'''
	возвращает 1 и выполняет команду в случае верной команды в переменной message 
	возвращает 0 в случае неудачной попытки
	'''
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		if message == '/auto':
			cur.execute("""INSERT INTO stack (user_id, type) 
				VALUES(?, ?)""", (ident, 0))
			cur.execute("""UPDATE students SET state = ? 
					WHERE user_id = ?""", ('swd', ident))
			return '0'

		if message == '/menu':
			cur.execute("""UPDATE students SET state = ? 
					WHERE user_id = ?""", ('menu', ident))
			return '0'

		if message[0] == '/':
			cur.execute("""SELECT count() FROM personal_w WHERE 
				user_id = ? AND workout_id = ?""", (ident, message[1:]))
			data = cur.fetchall()

			if (data[0][0] == 0):
				return '1'

			cur.execute("""INSERT INTO stack (user_id, type) 
				VALUES (?,?) """, (ident, int(message[1:])))
			cur.execute("""UPDATE students SET state = ? 
				WHERE user_id = ?""", ('swd', ident))
			return '0'

	return '2'


def check_date(ident, message):
	if message == '/today':
		now = datetime.datetime.now()
		return (str(now.day) + '.' + str(now.month) + '.' + str(now.year))
	check = message.split('.')
	cnt = 0
	for p in check:
		if p.isdigit():
			cnt += 1
	if len(check) != 3 or cnt != 3:
		return '-1'
	return message


def change_state(ident, message):
	""" функция меняющая состония и возвращающая 
	нужные сообщения

	"""
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT state FROM students WHERE user_id = ?""", (ident,))
		data = cur.fetchall()
		state = data[0][0]

		if state == 'expect_name':
			new_state = 'expect_birthday'
			cur.execute("""UPDATE students SET name = ?, 
				state = ? WHERE user_id = ?""", 
				(message, new_state, ident))
			return 'Напиши свою дату рождения в формате D.M.Y'

		elif state == 'expect_birthday':
			date = check_date(ident, message)
			if date == '-1':
				return ('Неверный формат ввода\n'
					'Напиши свою дату рождения в формате D.M.Y')

			new_state = 'expect_group'
			cur.execute("""UPDATE students SET birth_day = ?, 
				state = ? WHERE user_id = ?""", 
				(date, new_state, ident))

			return 'Напиши свою группу'

		elif state == 'expect_group':
			new_state = 'expect_weight'
			cur.execute("""UPDATE students SET group_ = ?, 
				state = ? WHERE user_id = ?""", 
				(message, new_state, ident))
			return 'Напиши свой Вес'

		elif state == 'expect_weight':
			new_state = 'expect_height'
			cur.execute("""UPDATE students SET weight = ?, 
				state = ? WHERE user_id = ?""", 
				(message, new_state, ident))
			return 'Напиши свой Рост'

		elif state == 'expect_height':
			new_state = 'menu'
			cur.execute("""UPDATE students SET height = ?, 
				state = ? WHERE user_id = ?""", 
				(message, new_state, ident))
			return ('end')

		elif state == 'menu':
			if message == '/diary':
				new_state = 'make_diary'
			elif message == '/workout':
				new_state = 'make_workout'
			else: 
				return '1'

			cur.execute("""UPDATE students SET state = ?
				WHERE user_id = ?""", 
				(new_state, ident))
			return '0'

		elif state == 'make_diary':
			return select_work(ident, message)

		elif state == 'swd':
			date = check_date(ident, message)
			if date == '-1':
				return ('1')
			cur.execute("""UPDATE stack SET date_ = ? 
				WHERE user_id = ? AND date_ = ?""", (date, ident, ''))
			cur.execute("""UPDATE students SET state = ? 
				WHERE user_id = ?""", 
				('get_add', ident))
			return '0'
		#get_add = get or add
		elif state == 'get_add':
			if message == '/get':
				cur.execute("""UPDATE students SET state = ? 
				WHERE user_id = ?""", 
				('menu', ident))
				return '0'
			elif message == '/more':
				if get_quantity_of_dates(ident) >= 4:
					cur.execute("""UPDATE students SET state = ? 
					WHERE user_id = ?""", 
					('menu', ident))
					return '0'
				else:
					cur.execute("""UPDATE students SET state = ? 
					WHERE user_id = ?""", 
					('make_diary', ident))
					return '0'
			else:
				return '1'


def get_state(ident) -> str:
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT state FROM students WHERE user_id = ?""", (ident,))
		data = cur.fetchall()
		if len(data) == 0:
			return 'no_such_user'
			
		state = data[0][0]
		if state == 'expect_day_or_trnum':
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", ('menu', ident))
		if state[0:3] == 'own':
			return 'generating_own_training'
		elif state == 'expect_day_or_trnum':
			return 'expect_day_or_trnum'
		elif state == 'expect_day_of_persworkout':
			return 'expect_day_of_persworkout'
		elif state == 'menu':
			return 'menu'
		elif state == 'make_diary':
			return 'make_diary'
		elif state == 'swd':
			return 'swd'
		elif state == 'get_add':
			return 'get_add'
		elif state == 'make_workout':
			return 'make_workout'
		else:
			return 'obtaining_personal_data'


def get_quantity_of_dates(ident):
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT count() as count FROM stack WHERE user_id = ?""", (ident,))
		data = cur.fetchall()
		return data[0][0]


def gen_diary_txt(ident):
	#соединение с текстовым файлом
	cnt = get_quantity_of_dates(ident)
	file_name = 'template' + str(cnt) + '.docx'
	if cnt >= 1:
		if cnt > 4:
			cnt = 4
		file_name = 'template' + str(cnt) + '.docx'
	else:
		doc = DocxTemplate("template1.docx")
		context = {'name' : "", 'birth_day' : "", 'group' : "", 'weight' : '', 'height' : ''}

		doc.render(context)
		doc.save("res_diary.docx")
		return

	doc = DocxTemplate(file_name)
	context = dict()

	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT name, birth_day, group_, weight, height 
			FROM students WHERE user_id = ?""", (ident, ))
		data_l_of_c = cur.fetchall()
		data = data_l_of_c[0]
		context['name'] = data[0]
		context['birth_day'] = data[1]
		context['group'] = data[2]
		context['weight'] = data[3]
		context['height'] = data[4]

	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT date_, type FROM stack WHERE user_id = ?""", (ident, ))
		data = cur.fetchall()

		day_number = 1
		for data_cortege in data:
			if day_number >= 5:
				break
			file_pl = 'date' + str(day_number)

			context[file_pl] = data_cortege[0]

			if data_cortege[1] == 0:
				enter_random_data_to_file(context, day_number);
			else:
				pass
				enter_own_workout_data_to_file(ident, context, day_number, data_cortege[1])

			day_number += 1
		cur.execute("""DELETE FROM stack WHERE user_id = ?""", (ident,))

	doc.render(context)
	doc.save("res_diary.docx")
	return


def enter_random_data_to_file(context, day_number):
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()

		file_pl = 'warmt' + str(day_number)
		cur.execute("""SELECT time_, content_ FROM random WHERE type_ = ?""", ('warm',))
		warm = cur.fetchall()
		num = random.randint(0, len(warm) - 1)
		st = 'Подготовительная часть ' + str(warm[num][0]) + ' мин:'
		context[file_pl] = st
		file_pl = 'warm' + str(day_number)
		context[file_pl] = warm[num][1]
		
		file_pl = 'maint' + str(day_number)
		cur.execute("""SELECT time_, content_ FROM random WHERE type_ = ?""", ('main',))
		main = cur.fetchall()
		num = random.randint(0, len(main) - 1)
		st = 'Основная часть ' + str(main[num][0]) + ' мин:'
		context[file_pl] = st
		file_pl = 'main' + str(day_number)
		context[file_pl] = main[num][1]

		file_pl = 'conclt' + str(day_number)
		cur.execute("""SELECT time_, content_ FROM random WHERE type_ = ?""", ('concl',))
		concl = cur.fetchall()
		num = random.randint(0, len(concl) - 1)
		st = 'Заключительная часть ' + str(concl[num][0]) + ' мин:'
		context[file_pl] = st
		file_pl = 'concl' + str(day_number)
		context[file_pl] = concl[num][1]


	file_pl = 'pulse_w' + str(day_number);
	context[file_pl] = random.randint(70, 90)
	
	file_pl = 'pulse_m' + str(day_number)
	context[file_pl] = random.randint(162, 180)
	
	file_pl = 'pulse_c' + str(day_number);
	context[file_pl] = random.randint(90, 110)
	
	#самоощущение
	feel = []
	feel.append("Усталость")
	feel.append("Нормальное")
	file_pl = 'feel' + str(day_number);
	context[file_pl] = feel[random.randint(0, len(feel) - 1)]

	#желание заниматься
	wish = []
	wish.append('+')
	wish.append('-')
	file_pl = 'w' + str(day_number);
	context[file_pl] = wish[random.randint(0, len(wish) - 1)]


def generation_your_own_workout(ident, message = ''):
	#функция генерации собственной тренировки
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT state FROM students WHERE user_id = ?""", (ident,))
		data = cur.fetchall()
		state = data[0][0]

		if state == 'make_workout':
			new_state = 'own_expect_warm_up_time'
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", 
				(new_state, ident))
			cur.execute("""SELECT count() FROM personal_w WHERE user_id = ?""", 
				(ident,))
			data = cur.fetchall()
			workout_id = data[0][0]
			cur.execute("""INSERT INTO personal_w (user_id, workout_id) 
				VALUES (?, ?)""", 
				(ident, workout_id + 1))
			return 'Укажите продолжительность разминочной части'

		cur.execute("""SELECT count() FROM personal_w WHERE user_id = ?""", 
				(ident,))
		data = cur.fetchall()
		workout_id = data[0][0]

		if state == 'own_expect_warm_up_time':
			if not message.isdigit():
				return 'Неверный формат ввода, введите количество минут (число)'
			new_state = 'own_expect_warm_up'
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", 
				(new_state, ident))
			cur.execute("""UPDATE personal_w SET warm_t = ? 
				WHERE user_id = ? AND workout_id = ?""",
				(int(message), ident, workout_id))
			return 'Распишите разминочную часть'

		if state == 'own_expect_warm_up':
			new_state = 'own_expect_main_part_time'
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", 
				(new_state, ident))
			cur.execute("""UPDATE personal_w SET warm = ? 
				WHERE user_id = ? AND workout_id = ?""",
				(message, ident, workout_id))
			return 'Укажите продолжительность основной части'

		if state == 'own_expect_main_part_time':
			if not message.isdigit():
				return 'Неверный формат ввода, введите количество минут (число)'
			new_state = 'own_expect_main_part'
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", 
				(new_state, ident))
			cur.execute("""UPDATE personal_w SET main_t = ? 
				WHERE user_id = ? AND workout_id = ?""",
				(int(message), ident, workout_id))
			return 'Распишите основную часть'

		if state == 'own_expect_main_part':
			new_state = 'own_expect_final_part_time'
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", 
				(new_state, ident))
			cur.execute("""UPDATE personal_w SET main = ? 
				WHERE user_id = ? AND workout_id = ?""",
				(message, ident, workout_id))
			return 'Укажите продолжительность заключительной части'

		if state == 'own_expect_final_part_time':
			if not message.isdigit():
				return 'Неверный формат ввода, введите количество минут (число)'
			new_state = 'own_expect_final_part'
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", 
				(new_state, ident))
			cur.execute("""UPDATE personal_w SET concl_t = ? 
				WHERE user_id = ? AND workout_id = ?""",
				(int(message), ident, workout_id))
			return 'Распишите заключительную часть'

		if state == 'own_expect_final_part':
			new_state = 'own_expect_name'
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", 
				(new_state, ident))
			cur.execute("""UPDATE personal_w SET concl = ? 
				WHERE user_id = ? AND workout_id = ?""",
				(message, ident, workout_id))
			return ('Укажите название этой тренировки, '
					'чтобы далее вы могли использовать ее повторно')

		if state == 'own_expect_name':
			new_state = 'menu'
			cur.execute("""UPDATE students SET state = ? WHERE user_id = ?""", 
				(new_state, ident))
			cur.execute("""UPDATE personal_w SET name = ? 
				WHERE user_id = ?  AND workout_id = ?""",
				(message, ident, workout_id))
			return ('end')
		return ('Произошла ошибка сейчас вы не можете '
			'генерировать собственную тренировку')


def query_t(ident, message):
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT count() FROM personal_w 
			WHERE user_id = ?""", (ident,))
		data = cur.fetchall()
		cnt = data[0][0]
		if message.isdigit() and (int(message) > 0 and int(message) <= cnt):
			cur.execute("""INSERT INTO stack (user_id, type) 
				VALUES (?, ?)""", (ident, int(message)))

			return 'Тренировка выбрана, укажите дату'
			#состояние ожидания даты или номера тренировки


def show_workouts(ident):
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT workout_id, name FROM personal_w 
			WHERE user_id = ?""", (ident,))
		data = cur.fetchall()
		if len(data) == 0:
			return '0'
		s = ''
		num = 1
		for training in data:
			s += '\n●' + ' /' + str(num) + ':' + training[1]
			num += 1
		return s


def enter_own_workout_data_to_file(ident, context, day_number, workout_id):
	# генерация по собственной тренировке
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute("""SELECT warm_t, warm, main_t, main, concl_t, concl
			FROM personal_w WHERE user_id = ? AND workout_id = ?""", 
			(ident, workout_id))
		data_l_of_c = cur.fetchall()
		data = data_l_of_c[0]


		file_pl = 'warmt' + str(day_number)
		context[file_pl] = ('Подготовительная часть ' + str(data[0]) + ' мин:')

		file_pl = 'warm' + str(day_number)
		context[file_pl] = (data[1])

		file_pl = 'maint' + str(day_number)
		context[file_pl] = ('Основная часть: ' + str(data[2]) + ' мин:')

		file_pl = 'main' + str(day_number)
		context[file_pl] = (str(data[3]))

		file_pl = 'conclt' + str(day_number)
		context[file_pl] = ('Заключительная часть ' + str(data[4]) + ' мин:')

		file_pl = 'concl' + str(day_number)
		context[file_pl] = (str(data[5]))

		file_pl = 'pulse_w' + str(day_number);
		context[file_pl] = random.randint(70, 90)

		file_pl = 'pulse_m' + str(day_number)
		context[file_pl] = random.randint(162, 180)
		
		file_pl = 'pulse_c' + str(day_number);
		context[file_pl] = random.randint(90, 110)
		
		#самоощущение
		feel = []
		feel.append("Усталость")
		feel.append("Хорошее")
		feel.append("Нормальное")
		file_pl = 'feel' + str(day_number);
		context[file_pl] = feel[random.randint(0, len(feel) - 1)]

		#желание заниматься
		wish = []
		wish.append('+')
		wish.append('-')
		file_pl = 'w' + str(day_number);
		context[file_pl] = wish[random.randint(0, len(wish) - 1)]

def delete_me(ident):
	with sqlite3.connect('students.sqlite') as db:
		cur = db.cursor()
		cur.execute('''SELECT * FROM students WHERE user_id = ?''', (ident, ))
		data = cur.fetchall()
		rec = data[0]
		cur.execute('''INSERT INTO del_users VALUES (?, ?, ?, ?, ?, ?, ?)''', rec)

		cur.execute('''DELETE FROM students WHERE user_id = ?''', (ident,))
		cur.execute('''DELETE FROM personal_w WHERE user_id = ?''', (ident,))
		cur.execute('''DELETE FROM stack WHERE user_id = ?''', (ident,))

