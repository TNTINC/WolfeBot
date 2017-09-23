import sqlite3, json

class Wolfe:

	def __init__(self, db):
		self.db = db

	def load(self, chat):

		chatid = chat.message['chat']['id']

		res = self.db.execute('SELECT * FROM chats WHERE id = ?', (chatid,)).fetchone()

		if not res:
			msg = chat.message
			params = {
				'id': msg['chat']['id'],
				'type': msg['chat']['type'],
				'first_name': msg['chat']['first_name'] if msg['chat']['first_name'] else None,
				'last_name': msg['chat']['last_name'] if msg['chat']['last_name'] else None,
				'username': msg['chat']['username'] if msg['chat']['username'] else None,
				'title': msg['chat']['title'] if msg['chat']['title'] else None
			}
			self.db.execute('INSERT INTO chats (id, first_name, last_name, title, username, type) VALUES (_)', (chatid,))
			self.db.commit()
			res = self.db.execute('SELECT * FROM chats WHERE id = ?', (chatid,)).fetchone()
		
		return res

	def clearChat(self, chat):
		chatid = chat.message['chat']['id']
		self.db.execute("UPDATE chats SET data = ?, action = NULL WHERE id = ?", ('{}', chatid))
		self.db.commit()

	def setAction(self, chat, action):
		chatid = chat.message['chat']['id']
		self.db.execute("UPDATE chats SET action = ? WHERE id = ?", (action, chatid))
		self.db.commit()

	def askNew(self, chat):

		# Get data from the db and add the data from the message
		data = self.getData(chat)

		if data['action']:
			d = {
				**json.loads(data['data']),
				data['action'].split(':')[-1]: chat.message['text'].split('/')[-1]
			}
		else:
			d = json.loads(data['data'])

		# Check if all the fields were filled
		for field, reply_text in self.NEW_VARS.items():

			# At least one field is empty, ask for value and return
			if not field in d:
				self.db.execute("UPDATE chats SET action = ?, data = ? WHERE id = ?", ('new:%s' % field, json.dumps(d), data['id']))
				self.db.commit()
				return chat.reply(reply_text)

		# Clear the data of the current chat and add the sticker pack
		self.clearChat(chat)

		c = self.db.cursor()
		c.execute('INSERT INTO packs (tg_id, name, ts_add) VALUES (:tg_id,:name,strftime(\'%s\', CURRENT_TIMESTAMP))', d)
		self.db.commit()

		return chat.reply('Perfect! Your sticker pack was added to the database, you can start adding stickers to the pack by pressing on /addstk_%s' % c.lastrowid)

if __name__ == "__main__":
	print('Murr~')
