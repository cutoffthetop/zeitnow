# -*- coding: utf-8 -*-
"""
	Project: Zeit Now
	Author: Nicolas Drebenstedt
	License: BSD, see LICENSE.md for details.
"""

from wsgiref.handlers import CGIHandler
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from google.appengine.api.channel import create_channel, send_message
from google.appengine.api.taskqueue import Task
from google.appengine.api.urlfetch import fetch
import json, urllib

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
					endpoint = 'channel_connected',
					methods = ['POST']
					)
				]
			)

	def fetch_zeit(self, url):
		from private import ZEIT_API_KEY
		resp = fetch(
			url = url,
			headers = {'X-Authorization': ZEIT_API_KEY}
			)
		return json.loads(resp.content)

	def fetch_twitter(self, topic):
		resp = fetch(
			url = 'http://search.twitter.com/search.json?rpp=3&q=' + topic
			)
		return json.loads(resp.content)

	def trigger_update(self, request):

		matches = self.fetch_zeit('http://api.zeit.de/content?limit=3')['matches']
		result = []
		for i in range(len(matches)):
			lead = self.fetch_zeit(matches[i]['uri'])
			tweets = self.fetch_twitter(urllib.quote(matches[i]['href']))['results']
			result.append(dict(lead = lead, tweets = tweets))
		
		send_message('1234', json.dumps(result))

		return Response(status = 204)

	def channel_connected(self, request):
		return Response(status = 204)

	def open_channel(self, request):

		client_id = request.values['client_id']
		token = create_channel(client_id)

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