# -*- coding: utf-8 -*-
"""
	Zeitnow
	~~~~~~~

	Author: Nicolas Drebenstedt
	License: BSD, see LICENSE.md for details.
"""

from wsgiref.handlers import CGIHandler
from werkzeug.wrappers import Request, Response


class Zeitnow(object):

	def dispatch_request(self, request):
		return Response('Hello Zeit!')

	def wsgi_app(self, environ, start_response):
		request = Request(environ)
		response = self.dispatch_request(request)
		return response(environ, start_response)

	def __call__(self, environ, start_response):
		return self.wsgi_app(environ, start_response)


def main():
	application = Zeitnow()
	CGIHandler().run(application)

if __name__ == '__main__':
	main()