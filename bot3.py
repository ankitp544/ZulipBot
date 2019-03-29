import pprint
import zulip
import sys
import re
import json
from random import randrange
import requests
from textblob import TextBlob 
from random import shuffle, choice
import sem

BOT_MAIL = "bruh-bot@chiru.zulipchat.com"

class ZulipBot(object):
	def __init__(self):
		self.client = zulip.Client(site="https://chiru.zulipchat.com/api/")
		self.subscribe()
		print("Initialised!")

	def subscribe(self):
		self.client.add_subscriptions([{"name": "Bruh"}])

	def get_query_category(self, content):
		score = -1
		chosen_category = -1
		keywords_for_categories = {
		0: ["hello", "hi", "hey"], #Greeting
		1: ["joke", "jokes"], #Joke
		2: ["quote", "quotes", "motivational", "inspirational"],
		3: ["news"]
		}
		regex = re.compile('[^a-zA-Z]')
		for category in keywords_for_categories:
			this_score = 0
			for word in content:
				if (regex.sub('', word)).lower() in keywords_for_categories[category]:
					this_score+=1
			this_score /= len(content)
			if this_score > score:
				score = this_score
				chosen_category = category
		return chosen_category

	def clean_message(self, message):
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", message).split())

	def is_message_extremely_negative(self, message):
		"""message = self.clean_message(message)
		print(message)
		analysis = TextBlob(message)
		print(analysis.sentiment.polarity)
		if analysis.sentiment.polarity < -0.4:
			return True
		return False
		"""
		x, y = sem.call(message)
		return x==-1 and y<-1


	def is_message_positive(self, message):
		"""
		message = self.clean_message(message)
		print(message)
		analysis = TextBlob(message)
		print(analysis.sentiment.polarity)
		if analysis.sentiment.polarity > 0.2:
			return True
		return False
		"""
		x,y = sem.call(message)
		return x==1


	def process(self, msg):
		content = msg["content"].split()
		sender_email = msg["sender_email"]

		if msg["display_recipient"]!="Bruh" or sender_email == BOT_MAIL:
			return

		print("Sucessfully heard.")

		query_category = self.get_query_category(content)
		#query_category = 2
		print(query_category)

		if (self.is_message_extremely_negative(msg['content'])):
			quotes_file = open("quotes.txt")
			quotes = quotes_file.read().splitlines()
			#print(quotes)
			self.client.send_message({
				"type": "stream",
				"subject": msg["subject"],
				"to": msg["display_recipient"],
				"content": "OMG! I think you should read this - \""  + quotes[randrange(len(quotes))] + "\""
			})
		elif query_category == 0: #Greeting
			replies = ["Heyya!", "Hello, I'm Bruh!", "Namaste!", "Hi!"]
			idx = randrange(len(replies))
			self.client.send_message({
				"type": "stream",
				"subject": msg["subject"],
				"to": msg["display_recipient"],
				"content": replies[idx]
			})
		elif query_category == 1: #Joke
			reply = requests.get("https://official-joke-api.appspot.com/jokes/random")
			joke = reply.json()
			#print(joke)
			self.client.send_message({
				"type": "stream",
				"subject": msg["subject"],
				"to": msg["display_recipient"],
				"content": joke['setup'] + '\n' + joke['punchline']
			})
		elif query_category == 2: #Quote of the day
			URL = "http://quotes.rest/qod.json"
			parameters = {'category': 'inspire'}
			reply = requests.get(url = URL, params = parameters)
			reply = reply.json()
			setup_line = ["", "Here's a quote for you!\n", "A wise man once said:\n"]
			self.client.send_message({
				"type": "stream",
				"subject": msg["subject"],
				"to": msg["display_recipient"],
				"content": setup_line[randrange(len(setup_line))] + reply['contents']['quotes'][0]['quote']
			})
		elif query_category == 3: #positive news
			URL = "https://newsapi.org/v2/top-headlines"
			parameters = {'apiKey' : '619dc2b423c142a29f4000799231a282', "from" : "2019-03-01", "to": "2019-03-16",
			'language': 'en'}
			reply = requests.get(url = URL, params = parameters)
			reply = reply.json()
			shuffle(reply['articles'])
			setup_line = "Here's a good news for you -"
			for article in reply['articles']:
				if (self.is_message_positive(article['title'])):
					self.client.send_message({
					"type": "stream",
					"subject": msg["subject"],
					"to": msg["display_recipient"],
					"content": setup_line[randrange(len(setup_line))] + article['title']
				})
					break


def main():
	bot = ZulipBot()
	bot.client.call_on_each_message(bot.process)

if __name__ == "__main__":
	main()