#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import cherrypy
from raven import Client
from cocktail.events import when
from woost import app
from woost.controllers import CMSController


def register(dsn):
    app.sentry = Sentry(Client(dsn))

    @when(CMSController.exception_raised)
    def handle_exception(event):
        error = event.exception
        is_http_error = isinstance(error, cherrypy.HTTPError)

        if (is_http_error and error.status == 500) or not is_http_error:
            app.sentry.capture_exception()


class Sentry(object):

    def __init__(self, client):
        self.client = client

    def get_data_from_request(self):
        """Returns request data extracted from cherrypy.request."""
        request = cherrypy.request
        return {
            'sentry.interfaces.Http': {
                'url': cherrypy.url(),
                'query_string': request.query_string,
                'method': request.method,
                'data': request.params,
                'headers': request.headers,
                'env': {
                    'SERVER_NAME': cherrypy.server.socket_host, 
                    'SERVER_PORT': cherrypy.server.socket_port
                }
            }
        }
    
    def capture_exception(self, exc_info=None, **kwargs):
        data = kwargs.get('data')
        if data is None:
            kwargs['data'] = self.get_data_from_request()

        return self.client.captureException(exc_info=exc_info, **kwargs)

    def capture_message(self, message, **kwargs):
        data = kwargs.get('data')
        if data is None:
            kwargs['data'] = self.get_data_from_request()

        return self.client.captureMessage(message, **kwargs)

