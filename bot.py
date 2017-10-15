import os, sqlite3, json, random, markovify, re, time
from colorama import init, Fore, Style
from aiotg import Bot


START_TIME = time.time()

# Count the number of handled requests via decorator
REQNUM = 0
def request(fn):
	def wrapper(*args, **kwargs):
		global REQNUM
		REQNUM += 1
		return fn(*args, **kwargs)
	return wrapper


with open("rp_data.txt", "r") as f:
    text = f.read()

text_model = markovify.NewlineText(text, state_size=2)
del text

vs = "V0.2"

CACHE_DIR = 'cache/'
RES_FOLDER = 'res/'

con = sqlite3.connect('wolfe.db')

bot = Bot(os.environ["API_TOKEN"])

basekeyboard = {'keyboard': [[{'text': '💡 Suggest'},{'text': '⭐️ Vote'}],[{'text': '⚠️ Report'},{'text': '🐾 Credits'}]], 'one_time_keyboard': True, 'resize_keyboard': True}

@bot.command(r"^\/(help|start)(\s*$|@WolfeLegacyBB?ot)") # Don't match commands aimed at other bots
async def welcome(chat, match):
	await chat.send_sticker(sticker="BQADAwADAgADZUASA3hbI2mGeTbkAg")
	await chat.send_text("\
		Hello, welcome to WolfeBot. This bot is not completely stable yet, so don't be alarmed if it stops working for a bit!\n\n\
		For further info please visit the channel @WolfeBotNews\n\
		Bug reports and feature requests ==> https://github.com/TNTINC/WolfeBot/issues \n\
		<em>If it goes absolutely haywire, throw a line at</em> @icefla", 
	parse_mode="HTML")
	return

@bot.command(r'^\/debugdump')
async def dump(chat, match):
	dbsize = len(con.execute("SELECT id FROM media").fetchall())
	db_amount_not_approved = len(
		con.execute("SELECT id FROM media WHERE approved = 0")
		.fetchall()
	)
	
	my_id = (await bot.get_me())["id"]

	# uptime
	m, s = divmod(time.time() - START_TIME, 60)
	h, m = divmod(m, 60)
	uptime_string = "%d:%02d:%02d" % (h, m, s)

	dump = \
	"""
	-- {time} --
	Wolfe {vs}
	{dbsize} images in database, {db_amount_not_approved} not approved.
	My id is {my_id}. Uptime is: {uptime}.
	{reqnum} requests handled.
	""".format(
		time = time.strftime("%a, %d %b %Y %H:%M:%S UTC"),
		vs = vs,
		dbsize = dbsize,
		db_amount_not_approved = db_amount_not_approved,
		my_id = my_id,
		uptime = uptime_string,
		reqnum = REQNUM 
	)
	return chat.reply(dump)

@bot.command(r'^fml')
def weather(chat, match):
	return chat.reply('*fucks your life*')

# Roleplay (owo)
@bot.command(r'\*(.+)\*')
@request
def roleplay(chat, match):
	if 'reply_to_message' in chat.message and chat.message['reply_to_message']['from']['id'] == 194903852:
		return chat.reply("*%s*" % text_model.make_short_sentence(200, tries=200).strip(" .*"))

# Respond to OwO appropriately
@bot.command(r'^OwO')
@request
def owo(chat, match):
	owo = ['whats this??', '*notices ur buldge*', '>//w//<', '*pounces on u*', '*sneaks in your bed and cuddles u*', '*nozzles u*', '*pounces on u and sinks his nozzle inside your fluffy fur*', '*scratches ur ears* x3']
	return chat.send_text(random.choice(owo))

# just why
@bot.command(r'^wolfe sieg')
@request
def owo(chat, match):
	owo = ['What the fuck is wrong with you', 'No.', 'Can we stop please?', 'Is it really necessary?','What about you stop?', 'WHY', 'I wish I didn\'t read tbh.', 'Uh, okay, i guess', 'No, no NO NO NO', 'I\'d rather not reply', 'Hitler was overrated tbh', 'True story bro']
	return chat.send_text(random.choice(owo))

# Stand up for self
@bot.command(r'^wolfe kys')
@request
def owo(chat, match):
	owo = ['No u', 'u', 'no', 'consider suicide', 'How can i kill myself if i\'m a bunch of bits?', 'why would i', 'i see no reason', 'uhm', 'thats okay', 'ehm', 'your fake and gay']
	return chat.send_text(random.choice(owo))

# Query the database for an image and send it
@bot.command(r'\/?yiff\s*$')
@request
async def yiff(chat, match):
	"""
	Send a random approved image from the database.
	"""

	r = con.execute('SELECT path, tg_id, id FROM media WHERE approved = 1 ORDER BY random() LIMIT 1').fetchone()

	keyboard = {'inline_keyboard': [[{'text': '👍', 'callback_data': 'lke_%s' % r[2]},{'text': '👎', 'callback_data': 'dke_%s' % r[2]},{'text': '❤️ Fav', 'callback_data': 'fav_%s' % r[2]}]]}

	# No need to reupload if image was already uploaded
	if r[1]:
		try:
			res = await chat.send_photo(photo=r[1]) #, reply_markup=json.dumps(keyboard))
		except RuntimeError:
			print("Failed sending cached image %s" % r[0])
		else:
			return

	with open("%s%s" % (RES_FOLDER, r[0]), 'rb') as f:
		tres = await chat.send_photo(f) #, reply_markup=json.dumps(keyboard))

	if tres['ok']:
		con.execute('UPDATE media SET tg_id = ? WHERE path = ?', (tres['result']['photo'][-1]['file_id'], r[0]))
		con.commit()

# If someone replies "fullsize" to an image we've sent, send the full image uncompressed
@bot.command(r'^(\/?)fullsize')
@request
async def fullsize(chat, match):
	"""
	Send the full version of an image
	"""
	if 'reply_to_message' in chat.message and 'photo' in chat.message['reply_to_message']:
		pid = chat.message['reply_to_message']['photo'][-1]['file_id']

		res = con.execute('SELECT path FROM media WHERE tg_id = ?', (pid,)).fetchone()
		if res:
			with open("%s%s" % (RES_FOLDER, res[0]), 'rb') as f:
				a = await chat.send_document(f, caption='Here you go!')
	return

# Flag an image for moderation
@bot.command(r'^(\/?)delete')
def disapprove(chat, match):
	"""
	Flag an image for moderation.

	Delete the image message, set the approved status of it to 0 in the database and notify @icefla.
	"""
	if 'reply_to_message' in chat.message \
		and 'photo' in chat.message["reply_to_message"]:
		pid = chat.message['reply_to_message']['photo'][-1]['file_id']
		res = con.execute('SELECT path, id FROM media WHERE tg_id = ?', (pid,)).fetchone()
		if res:
			print('[WARN] Soft deleting %s !!!' % res[0])
			chat.reply("Deleting...")
			
			# Delete the message
			bot.api_call("deleteMessage",
				chat_id = chat.message["chat"]["id"],
				message_id = chat.message["reply_to_message"]["message_id"]
			)

			# Set the photo's approved state to false
			con.execute(
				'UPDATE media SET approved = 0 WHERE tg_id = ?', 
				(pid,)
			)
			con.commit()

			# Notify @icefla
			bot.api_call("sendMessage",
				text="Something was flagged! : %s : %s" % (res[1],res[0]),
				chat_id="-262778980"
			)

		else:
			return chat.reply('This image doesn\'t exist!')


@bot.command(r"^\/?id (.*)$")
def send_image_by_id(chat, match):
	try:
		photo_id = int(match[1])
	except:
		return

	r = con.execute(
		'SELECT tg_id, path FROM media WHERE id = ?', 
		(photo_id,)
	).fetchone()

	if r:
		tg_id = r[0]
		path = r[1]
		try:
			print("Sent photo %s from cache" % match[1])
			return chat.send_photo(photo=tg_id)
		except:
			print("Sent photo %s from disk" % match[1])
			return chat.send_photo("%s%s" % (RES_FOLDER,path))
	else:
		return chat.reply("Image not found")

# wolfe yiff me
@bot.command(r'^wolfe (.+) me')
@request
def roleplay(chat, match):
	return chat.send_text('*%ss %s*' % (match.group(1), chat.message['from']['first_name']))

# <3
@bot.command('who\'s keo?')
def keo(chat, match):
	return chat.send_text('A really really cute fox!')

# Praise the bulge
@bot.command('bulge')
def bulge(chat, match):
	if 'reply_to_message' in chat.message and chat.message['reply_to_message']['from']['id'] == 194903852:
		keyboard = {'inline_keyboard': [[{'text': '🍆', 'url': 'https://t.me/bulge'},{'text': '🍆', 'url': 'https://t.me/bulge'},{'text': '🍆', 'url': 'https://t.me/bulge'},{'text': '🍆', 'url': 'https://t.me/bulge'},{'text': '🍆', 'url': 'https://t.me/bulge'}]]}
		return chat.send_text(random.choice(['Did someone say bulge?','*notices your buldge*', 'OwO', 'Murr~', 'Bulge?', 'I happen to have a lot of bulges.']), reply_markup=json.dumps(keyboard))

@bot.inline
@request
def inline(request):
	"""
	Handle inline requests by allowing the user to choose from a grid of random images
	"""
	r = con.execute(
		'SELECT tg_id, id FROM media WHERE tg_id IS NOT NULL AND approved = 1 '
		'ORDER BY random() LIMIT 25'
	).fetchall()

	return request.answer(
		results=
			[{
				'type': 'photo', 
				'id': str(pic[1]), 
				'photo_file_id': pic[0]
			} for pic in r], 
		cache_time=0, 
		is_personal=True, 
		next_offset='Yolo'
	)

if __name__ == '__main__':
	bot.run()

