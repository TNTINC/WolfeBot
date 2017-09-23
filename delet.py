import os, sqlite3, json, random, markovify, re
from colorama import init, Fore, Style
from aiotg import Bot

bot = Bot(os.environ["API_TOKEN"])

@bot.command('.')
async def msg(chat, match):
	m = chat.message

	if m['chat']['type'] == 'channel':
		return

	if chat.message['chat']['type'] in ['group', 'supergroup']:
		print(Fore.CYAN + "(%s) [%s]" % (m['chat']['id'], m['chat']['title']) + Style.RESET_ALL)

	await bot.api_call('forwardMessage', chat_id=m['chat']['id'], from_chat_id='@WolfebotNews', message_id=28, disable_notification='True')

	if chat.message['chat']['type'] in ['group', 'supergroup']:
		return bot.api_call('leaveChat', chat_id=m['chat']['id'])
	else:
		return

	#return bot.api_call('forwardMessage', chat_id='-183777017', from_chat_id=m['chat']['id'], message_id=m['message_id'], disable_notification='True')

if __name__ == '__main__':
	bot.run()

