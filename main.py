# Бот который будет собирать информацию о том когда человек был в сети
import vk_api # API для работы с вк
import time as t
import json
import requests
import xlsxwriter
import os
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Создаем сообщество в вк
# Получение токена:
# Заходим в управление
# Настройки -> Работа с API -> Создать ключ -> Создаем токен с доступом к сообщениям
# Токен группы:
token = '1928f15385b14c139d346aaf010254c0d2071585ef9a9b3767896f5135ee748d01daeb2e38c0b980db0e7'
admin_id = 220584065 # ID админа
group_id = 197653027
# Вход в вк с токеном группы
vk = vk_api.VkApi(token = token)
vk._auth_token()

platforms = {
	"1": "Мобильная версия",
	"2": "Приложение для iPhone",
	"3": "Приложение для iPad",
	"4": "Приложение для Android",
	"5": "Приложение для Windows Phone",
	"6": "Приложение для Windows 10",
	"7": "Полная версия сайта"
}
def convert_UNIX_date_in_normal_date(unix_time): # Функция перевода unix time в стандартную дату
	
		return t.strftime("%d.%m.%Y %H:%M:%S gmt+7", t.gmtime(unix_time+(7*60*60)))
def write_json(file_name, data): # </Запись в JSON>
	with open(file_name, "w", encoding='utf-8' ) as f:
		json.dump(data, f, indent = 2, ensure_ascii = False)
def load_json(file_name): # </Загрузка из JSONа>
	with open(file_name, 'r', encoding='utf-8') as f:
		data = json.load(f)
	return data
def ids_to_str(ids):
	str_ids = ''
	for user_id in user_ids:
		str_ids += str(user_id) + ','
	str_ids = str_ids[:-1]
	return str_ids
def update_json(file_name, data):
	users = data
	# users2 = load_json("b.json")
	rez = load_json(file_name)
	changes = False
	for user in users:
		if list(rez.keys()).count(str(user["id"])) > 0:
			seens = rez[str(user["id"])]["seens"]
			time = user["last_seen"]["time"]
			platform = user["last_seen"]["platform"]
			if user["last_seen"]["time"] != rez[str(user["id"])]["seens"][-1]["time"]:
				changes = True
				seens.append(
					{
						"get_seen": int(t.time()),
						"time": user["last_seen"]["time"],
						"n_time": convert_UNIX_date_in_normal_date(user["last_seen"]["time"]),
						"platform": user["last_seen"]["platform"],
						"ruPlatform": platforms[str(user["last_seen"]["platform"])]
					}
				)
				rez.update(
					{
						str(user["id"]):{
							"first_name": user["first_name"],
							"last_name": user["last_name"],
							"seens":seens
						}
					}
				)
		else:
			changes = True
			rez.update(
				{
					str(user["id"]):{
						"first_name": user["first_name"],
						"last_name": user["last_name"],
						"seens":[
							{
								"get_seen": int(t.time()),
								"time": user["last_seen"]["time"],
								"n_time": convert_UNIX_date_in_normal_date(user["last_seen"]["time"]),
								"platform": user["last_seen"]["platform"],
								"ruPlatform": platforms[str(user["last_seen"]["platform"])]
							}
						]
					}
				}
			)
	if changes:
		write_json(file_name, rez)
		print('Изменения есть')
	else:
		print('Изменений нет')
def createXLSX(data, XLSXFile):

	workbook = xlsxwriter.Workbook(XLSXFile)

	Roboto14 = workbook.add_format()

	for user in data:
		worksheet = workbook.add_worksheet(data[user]["first_name"]+' '+data[user]["last_name"])
		worksheet.set_column('A:A', 24)
		worksheet.set_column('B:B', 32)
		worksheet.set_column('C:C', 15)
		worksheet.set_column('D:D', 15)
		worksheet.set_column('F:F', 15)
		worksheet.set_column('G:G', 40)
		worksheet.set_column('H:H', 40)
		worksheet.write('A1', 'Был в сети', Roboto14)
		worksheet.write('B1', 'Платформа', Roboto14)
		worksheet.write('C1', 'Проверка UNIX', Roboto14)
		worksheet.write('D1', 'Был в сети UNIX', Roboto14)
		
		worksheet.write('F1', 'id', Roboto14)
		worksheet.write('F2', user, Roboto14)

		worksheet.write('G1', 'Имя', Roboto14)
		worksheet.write('G2', data[user]["first_name"], Roboto14)

		worksheet.write('H1', 'Фамилия', Roboto14)
		worksheet.write('H2', data[user]["last_name"], Roboto14)

		seens = data[user]["seens"]
		seens.reverse()
		i = 1
		for seen in seens:
			i += 1
			worksheet.write('A'+str(i), seen["n_time"], Roboto14)
			worksheet.write('B'+str(i), seen["ruPlatform"], Roboto14)
			worksheet.write('C'+str(i), seen["get_seen"], Roboto14)
			worksheet.write('D'+str(i), seen["time"], Roboto14)
	workbook.close()
def delete(file_name):
	path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
	os.remove(path)
user_ids = load_json("user_ids.json")
t0 = t.time()
users = vk.method(
	'users.get',
	{
		'user_ids': ids_to_str(user_ids),
		'fields':'first_name,last_name,last_seen'
	}
)
update_json("data.json", users)
while True:
	# получаем последнее сообщение пльзователя (если оно не отвечено)
	messages_unanswered = vk.method(
		"messages.getConversations", 
		{
			"filter": "unanswered"
		}
	)
	# если неотвеченых сообщений >=1
	if messages_unanswered['count'] >= 1:
		# последнее сообщение
		last_message = messages_unanswered['items'][0]['last_message']
		# получаем id пользователя от которого пришло сообщение
		peer_id = last_message['peer_id']
		if peer_id == admin_id:
			if last_message["text"].lower().count("добавить: "):
				add_user = last_message["text"].lower()
				add_user = add_user.replace('добавить: ', '')
				if add_user.isdigit():
					add_user = int(add_user)
					if user_ids.count(add_user) == 0:
						user_ids.append(add_user)
						write_json('user_ids.json', user_ids)
						info = vk.method(
							"users.get",
							{
								"user_ids": add_user,
								'fields':'first_name,last_name,last_seen,sex'
							}
						)
						if info[0]["sex"]==1:
							info[0]["sex"]='a'
						else:
							info[0]["sex"]=''
						text = 'В слежку добавлен{sex}: [id{user_id}|{first_name} {last_name}]'.format(
							sex=info[0]["sex"],
							user_id = add_user,
							first_name = info[0]["first_name"],
							last_name = info[0]["last_name"]
						)
						vk.method(
							"messages.send",
							{
								"peer_id":peer_id,
								"message":text,
								"random_id":0
							}
						)
					else:
						info = vk.method(
							"users.get",
							{
								"user_ids": add_user,
								'fields':'first_name,last_name',
								"name_case":"ins"
							}
						)
						text = 'Мы уже следим за [id{user_id}|{first_name} {last_name}]'.format(
							user_id = add_user,
							first_name = info[0]["first_name"],
							last_name = info[0]["last_name"]
						)
						vk.method(
							"messages.send",
							{
								"peer_id":peer_id,
								"message":text,
								"random_id":0
							}
						)
				else:
					vk.method(
						"messages.send",
						{
							"peer_id":peer_id,
							"message":'Не верный id',
							"random_id":0
						}
					)
			elif last_message["text"].lower().count("удалить: "):
				remove_user = last_message["text"].lower()
				remove_user = remove_user.replace('удалить: ', '')
				if remove_user.isdigit():
					remove_user = int(remove_user)
					if user_ids.count(remove_user) > 0:
						user_ids.remove(remove_user)
						write_json('user_ids.json', user_ids)
						info = vk.method(
							"users.get",
							{
								"user_ids": remove_user,
								'fields':'first_name,last_name,last_seen,sex'
							}
						)
						if info[0]["sex"]==1:
							info[0]["sex"]='a'
						else:
							info[0]["sex"]=''
						text = 'Из слежки удален{sex}: [id{user_id}|{first_name} {last_name}]'.format(
							sex=info[0]["sex"],
							user_id = remove_user,
							first_name = info[0]["first_name"],
							last_name = info[0]["last_name"]
						)
						vk.method(
							"messages.send",
							{
								"peer_id":peer_id,
								"message":text,
								"random_id":0
							}
						)
					else:
						info = vk.method(
							"users.get",
							{
								"user_ids": remove_user,
								'fields':'first_name,last_name',
								"name_case":"ins"
							}
						)
						text = 'Мы ещё не следили за [id{user_id}|{first_name} {last_name}]'.format(
							user_id = remove_user,
							first_name = info[0]["first_name"],
							last_name = info[0]["last_name"]
						)
						vk.method(
							"messages.send",
							{
								"peer_id":peer_id,
								"message":text,
								"random_id":0
							}
						)
				else:
					vk.method(
							"messages.send",
							{
								"peer_id":peer_id,
								"message":'Не верный id',
								"random_id":0
							}
						)
			elif last_message["text"].lower() == 'слежка':
				text = 'Слежка:\n'
				info = vk.method(
					"users.get",
					{
						"user_ids": ids_to_str(user_ids),
						'fields':'first_name,last_name,last_seen'
					}
				)
				for i in info:
					text += '[id{user_id}|{first_name} {last_name}]\n'.format(
						user_id = i["id"],
						first_name = i["first_name"],
						last_name = i["last_name"]
					)
				vk.method(
					"messages.send",
					{
						"peer_id":peer_id,
						"message":text,
						"random_id":0
					}
				)
			elif last_message["text"].lower() == 'файл':
				pass
				# Отправка файла
				# Загрузка документа
				upload = vk_api.VkUpload(vk)
				doc1 = upload.document_message(
					doc = "data.json",
					title = "data.json",
					peer_id = peer_id
				)
				createXLSX(load_json("data.json"), "data.xlsx")
				doc2 = upload.document_message(
					doc = "data.xlsx",
					title = "data.xlsx",
					peer_id = peer_id
				)
				doc3 = upload.document_message(
					doc = "user_ids.json",
					title = "user_ids.json",
					peer_id = peer_id
				)
				delete("data.xlsx")
				# Отправка документа
				vk.method(
					"messages.send",
					{
						"peer_id":peer_id,
						"attachment":'doc{owner_id1}_{media_id1},doc{owner_id2}_{media_id2},doc{owner_id3}_{media_id3}'.format(
							owner_id1=doc1["doc"]["owner_id"],
							media_id1=doc1["doc"]['id'],
							owner_id2=doc2["doc"]["owner_id"],
							media_id2=doc2["doc"]['id'],
							owner_id3=doc3["doc"]["owner_id"],
							media_id3=doc3["doc"]['id']
						),
						"random_id":0
					}
				)
			else:
				keyboard = VkKeyboard(one_time = False)
				keyboard.add_button("Слежка")
				keyboard.add_button("Файл")
				keyboard = keyboard.get_keyboard()
				vk.method(
					"messages.send",
					{
						"peer_id":peer_id,
						"message":"""Добавить: {id пользователя} - добавляет пользователя по id в слежку
						Удалить: {id пользователя} - удаляет пользователя по id из слежки
						Слежка - Возвращает пользователей за которыми ведется слежка
						файл - присылает файл с временем посещения всех пользователей""",
						"keyboard": keyboard,
						"random_id":0
					}
				)
		else:
			vk.method(
				"messages.send",
				{
					"peer_id":peer_id,
					"message":'Я разговариваю только с админом)',
					"random_id":0
				}
			)
	t1 = t.time()
	if t1-t0 > 30:
		users = vk.method(
			'users.get',
			{
				'user_ids': ids_to_str(user_ids),
				'fields':'first_name,last_name,last_seen'
			}
		)
		update_json("data.json", users)
		t0 = t.time()