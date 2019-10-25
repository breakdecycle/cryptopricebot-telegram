import logging
import os
import random
import re
import time

import requests
import telepot
from telepot.loop import MessageLoop

# market=btc-xem
from util.logger import log_setup


def main():
	MessageLoop(bot, handle).run_as_thread()
	logger.info('Listening...')

	while 1:
		# Randomising wait time to mimic humans!
		time.sleep(random.randint(5, 10))
	logger.info('I am done.')


def handle(msg):
	"""Handle messages received by bot"""
	content_type, chat_type, chat_id = telepot.glance(msg)
	# logger.info(content_type, chat_type, chat_id)
	logger.info('Chat ID: {}   Message: {}'.format(chat_id, msg['text']))

	# To make sure user input is text
	if content_type == 'text':
		userMsg = msg['text']
		pairingRegex = re.findall("[A-z]{3,5}-[A-z]{2,5}", userMsg)

		addRegex = re.match("/add", userMsg)
		removeRegex = re.match("/remove", userMsg)
		showRegex = re.match("/show", userMsg)
		priceRegex = re.match("/p", userMsg)

		lunoRegex = re.search("luno", userMsg.lower())
		quoineRegex = re.search("quoine", userMsg.lower())

		if userMsg.lower() == 'check all':
			for pair in coinList:
				params = {'market': pair}

				if pair.startswith('BTC'):
					r=requests.get('https://bittrex.com/api/v1.1/public/getticker', params=params)
					price = r.json()['result']['Bid']
					formatted_price = '{0:.8f}'.format(price)
					priceUSD = price*priceBTC
					formatted_priceUSD = '{0:.2f}'.format(priceUSD)
					priceMYR = priceUSD*usdMYR
					formatted_priceMYR = '{0:.2f}'.format(priceMYR)

					bot.sendMessage(chat_id,'{}: \n*{}*BTC  \n*{}*USD  *{}*MYR'.format(pair, formatted_price, formatted_priceUSD, formatted_priceMYR), parse_mode='Markdown')

				elif pair.startswith('USDT'):
					r=requests.get('https://bittrex.com/api/v1.1/public/getticker', params=params)
					price = r.json()['result']['Bid']
					formatted_price = '{0:.2f}'.format(price)
					priceMYR = '{0:.2f}'.format(price*usdMYR)

					bot.sendMessage(chat_id,'{}: \n*{}*USDT  *{}*MYR'.format(pair, formatted_price, priceMYR), parse_mode='Markdown')

				elif pair.startswith('LUNO'):
					luno = requests.get('https://api.mybitx.com/api/1/ticker?pair=XBTMYR')
					priceLuno = luno.json()['bid']

					bot.sendMessage(chat_id,'{}: *{}*MYR'.format(pair, priceLuno), parse_mode='Markdown')

				elif pair.startswith('QUOINE'):
					quoineJ = requests.get('https://api.quoine.com/products/5')
					priceJPY = quoineJ.json()['market_bid']
					formatted_price = '{0:.2f}'.format(priceJPY)
					priceUSD = '{0:.2f}'.format(priceJPY*jpyUSD)
					priceMYR = '{0:.2f}'.format(priceJPY*jpyMYR)

					bot.sendMessage(chat_id,'{} : \n*{}*JPY  \n*{}*USD  *{}*MYR'.format(pair, formatted_price, priceUSD, priceMYR), parse_mode='Markdown')

				else:
					r=requests.get('https://bittrex.com/api/v1.1/public/getticker', params=params)
					price = r.json()['result']['Bid']
					formatted_price = '{0:.2f}'.format(price)

					bot.sendMessage(chat_id,'{} : *{}*'.format(pair, formatted_price), parse_mode='Markdown')


		elif addRegex != None or removeRegex != None or showRegex != None:
			if chat_id == int(admin):
				if addRegex != None:
					if len(pairingRegex ) > 0 :
						for pair in pairingRegex:
							PAIR = pair.upper()
							coinList.append(PAIR)
							bot.sendMessage(chat_id,'Added {} to coinList!'.format(PAIR))

					else:
						bot.sendMessage(chat_id,'Please include what pairings you would like to add into coinList.')

				
				elif removeRegex != None:
					if len(pairingRegex ) > 0 :
						for pair in pairingRegex:
							PAIR = pair.upper()
							if PAIR in coinList:
								coinList.remove(PAIR)
								bot.sendMessage(chat_id,'Removed {} from coinList!'.format(PAIR))
							else:
								bot.sendMessage(chat_id,'{} cannot be removed as it is not in the list to begin with.'.format(PAIR))
				
				else:
					bot.sendMessage(chat_id, str(coinList))

			else:
				bot.sendMessage(chat_id,'Sorry I do not understand you')
				logger.info(admin)
				logger.info('chat_id is {}. It is of type: {}'.format(chat_id, type(chat_id)))

		# Regex to sort out crypto pairings from user input
		elif len(pairingRegex ) > 0 or priceRegex != None:

			if len(pairingRegex ) > 0:
				for pair in pairingRegex:
					# change all to upper case for standardisation
					PAIR = pair.upper()
					# input crypto pairing as parameter in api url (bittrex)
					params= {'market' : PAIR}

					# try in case of invalid crypto pairings
					try:
						if PAIR.startswith('BTC'):
							r=requests.get('https://bittrex.com/api/v1.1/public/getticker', params=params)
							price = r.json()['result']['Bid']
							formatted_price = '{0:.8f}'.format(price)
							priceUSD = price*priceBTC
							formatted_priceUSD = '{0:.2f}'.format(priceUSD)
							priceMYR = priceUSD*usdMYR
							formatted_priceMYR = '{0:.2f}'.format(priceMYR)

							bot.sendMessage(chat_id,'{}: \n*{}*BTC  \n*{}*USD  *{}*MYR'.format(PAIR, formatted_price, formatted_priceUSD, formatted_priceMYR), parse_mode='Markdown')

						elif PAIR.startswith('USDT'):
							r=requests.get('https://bittrex.com/api/v1.1/public/getticker', params=params)
							price = r.json()['result']['Bid']
							formatted_price = '{0:.2f}'.format(price)
							priceMYR = '{0:.2f}'.format(price*usdMYR)

							bot.sendMessage(chat_id,'{}: \n*{}*USDT  *{}*MYR'.format(PAIR, formatted_price, priceMYR), parse_mode='Markdown')

					# send prompt in case of invalid crypto pairing	
					except:
						bot.sendMessage(chat_id,'Please key in a valid currency pair (i.e. btc-xem, usdt-btc, etc)')

			if priceRegex != None:

				if lunoRegex != None:
					luno = requests.get('https://api.mybitx.com/api/1/ticker?pair=XBTMYR')
					priceLuno = luno.json()['bid']

					bot.sendMessage(chat_id,'LUNO: *{}*MYR'.format(priceLuno), parse_mode='Markdown')

				if quoineRegex != None:
					quoineJ = requests.get('https://api.quoine.com/products/5')
					priceJPY = quoineJ.json()['market_bid']
					formatted_price = '{0:.2f}'.format(priceJPY)
					priceUSD = '{0:.2f}'.format(priceJPY*jpyUSD)
					priceMYR = '{0:.2f}'.format(priceJPY*jpyMYR)

					bot.sendMessage(chat_id,'QUOINE : \n*{}*JPY  \n*{}*USD  *{}*MYR'.format(formatted_price, priceUSD, priceMYR), parse_mode='Markdown')

				else:
					bot.sendMessage(chat_id, 'Please include an argument for /p. Choice of either *LUNO* or *QUOINE*.', parse_mode='Markdown')

		# send prompt as did not manage to find any crypto pairing in user's input
		else:
			bot.sendMessage(chat_id,'Please key in a valid currency pair (i.e. btc-xem, usdt-btc, etc)')

# Testing pit - to be commented out otherwise ##################

		# msgList = msg['text'].split(" ")

		# i=0

		# while i<len(msgList):
		# 	bot.sendMessage(chat_id, msgList[i])
		# 	i += 1

# Testing pit- to be commented out otherwise ##################


if __name__ == '__main__':
	# Global variables
	LOGGER_LEVEL = logging.INFO  # TODO: Set logging level | Options: 'INFO', 'DEBUG', 'ERROR', etc.

	PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
	SCRIPT_NAME = os.path.basename(__file__)[:-3]
	LOG_FILENAME = SCRIPT_NAME
	logger = log_setup(PARENT_DIR, LOG_FILENAME, LOGGER_LEVEL)

	token = os.getenv('CryptoPBot_Telegram')
	admin = os.getenv('adminID')

	bot = telepot.Bot(token)
	me = bot.getMe()
	logger.info('Initialized bot: {}'.format(me.get('username')))

	coinList = ['USDT-BTC', 'QUOINE', 'LUNO', 'BTC-ETH', 'BTC-LTC', 'BTC-XMR']

	xrate = requests.get('https://api.fixer.io/latest?base=USD')
	usdMYR = xrate.json()['rates']['MYR']

	xrateJPY = requests.get('https://api.fixer.io/latest?base=JPY')
	jpyMYR = xrateJPY.json()['rates']['MYR']
	jpyUSD = xrateJPY.json()['rates']['USD']

	bittBTC = requests.get('https://bittrex.com/api/v1.1/public/getticker?market=usdt-btc')
	priceBTC = bittBTC.json()['result']['Bid']
	
	main()
