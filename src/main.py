# -*- coding: utf-8 -*-
"""
	Project: Zeit Now
	Author: Nicolas Drebenstedt
	License: BSD, see LICENSE.md for details.
"""

from google.appengine.api.channel import create_channel, send_message
from google.appengine.api.taskqueue import Task
from google.appengine.api.urlfetch import fetch
from google.appengine.ext import ndb
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from wsgiref.handlers import CGIHandler
import logging, json, urllib

try:
	from private import ZEIT_API_KEY
except ImportError:
	ZEIT_API_KEY = 'no-key-available'

ZEIT_BASE_URL = 'http://api.zeit.de/content'
TWITTER_BASE_URL = 'http://search.twitter.com/search.json'


class Client(ndb.Model):
	timestamp = ndb.DateTimeProperty(auto_now = True)


class Zeitnow(object):

	def __init__(self):
		self.url_map = Map(
			strict_slashes = False,
			rules = [
				Rule(
					string = '/api/update',
					endpoint = 'trigger_update',
					methods = ['POST']
					),
				Rule(
					string = '/api/channel',
					endpoint = 'open_channel',
					methods = ['POST']
					),
				Rule(
					string = '/_ah/channel/connected',
					endpoint = 'connect_channel',
					methods = ['POST']
					),
				Rule(
					string = '/_ah/channel/disconnected',
					endpoint = 'disconnect_channel',
					methods = ['POST']
					)
				]
			)

	def fetch_url(self, url, headers = {}, params = {}):
		resp = fetch(
			headers = headers,
			url = url + '?' + urllib.urlencode(params)
			)
		return json.loads(resp.content)

	def fetch_zeit(self, url = ZEIT_BASE_URL):
		return self.fetch_url(
			url = url,
			headers = {'X-Authorization': ZEIT_API_KEY},
			params = dict(
				limit = 3
				)
			)

	def fetch_twitter(self, query):
		return self.fetch_url(
			TWITTER_BASE_URL,
			params = dict(
				q = query
				)
			)['results']

	def broadcast_message(self, message):
		for client in Client.query().iter():
			send_message(client.key.id(), message)

	def trigger_update(self, request):

		def aggregate(matches):
			"""
			for i in range(len(matches)):
				lead = self.fetch_zeit(matches[i]['uri'])
				tweets = self.fetch_twitter(matches[i]['href'])
				yield dict(lead = lead, tweets = tweets)"""
			for match in matches:
				lead = self.fetch_zeit(match['uri'])
				tweets = self.fetch_twitter(match['href'])
				yield dict(lead = lead, tweets = tweets)
			
		matches = self.fetch_zeit()['matches']
		result = list(aggregate(matches))
		self.broadcast_message(json.dumps(result))

		return Response(status = 204)

	def connect_channel(self, request):
		Client(id = request.values['from']).put()
		return Response(status = 204)

	def disconnect_channel(self, request):
		ndb.Key(Client, request.values['from']).delete()
		return Response(status = 204)

	def open_channel(self, request):

		client_id = request.values['client_id']
		token = create_channel(client_id, duration_minutes=5)

		Task(url = '/api/update', countdown = 2).add()
		
		return Response(json.dumps({'channel': token}))

	def __call__(self, environ, start_response):
		
		request = Request(environ)
		adapter = self.url_map.bind_to_environ(environ)
		endpoint, values = adapter.match()
		response = getattr(self, endpoint)(request)

		return response(environ, start_response)


def main():
	application = Zeitnow()
	CGIHandler().run(application)

if __name__ == '__main__':
	main()