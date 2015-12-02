# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Pepe Osca <pepe.osca@whads.com>
"""
import json
import urllib

import cherrypy
from cocktail.controllers import Controller, Location, session
from woost import app
from woost.controllers import CMSController
from .identityprovider import FacebookIdentityProvider

SESSION_PREFIX = "woost.extensions.identity.facebook."


class FacebookOAuthController(Controller):
    def resolve(self, path):

        if not path:
            raise cherrypy.HTTPError(400)

        provider_id = path[0]

        try:
            provider_id = int(provider_id)
        except ValueError:
            raise cherrypy.HTTPError(400)

        provider = FacebookIdentityProvider.get_instance(provider_id)
        if provider is None:
            raise cherrypy.NotFound()

        path.pop(0)
        return FacebookOAuthProviderController(provider)


class FacebookOAuthProviderController(Controller):
    def __init__(self, provider):
        Controller.__init__(self)
        self.provider = provider
        self.target_url = (
            session.get(SESSION_PREFIX + "target_url")
            or app.website.home.get_uri()
        )

    def step_url(self, step_number):
        location = Location.get_current_host()
        location.path_info = "/facebook_oauth/%d/step%d" % (
            self.provider.id,
            step_number
        )
        return unicode(location).decode("utf-8")

    @cherrypy.expose
    def step1(self, code = None, target_url = None, **kwargs):

        self.check_step1_errors(**kwargs)

        if target_url:
            self.target_url = target_url
            session[SESSION_PREFIX + "target_url"] = target_url

        if not code:
            params = {
                'client_id': self.provider.client_id,
                'redirect_uri': self.step_url(1),
                'scope': ','.join(self.provider.scope)
            }
            login_uri = 'https://www.facebook.com/dialog/oauth?' + \
                        urllib.urlencode(params)

            raise cherrypy.HTTPRedirect(login_uri)

        params = {
            'client_id': self.provider.client_id,
            'redirect_uri': self.step_url(1),
            'client_secret': self.provider.client_secret,
            'code': code
        }
        token_uri = 'https://graph.facebook.com/v2.3/oauth/access_token?' \
                    + urllib.urlencode(params)

        json_file = urllib.urlopen(token_uri).readline()
        token_data = json.loads(json_file)

        session[SESSION_PREFIX + "credentials"] = token_data

        raise cherrypy.HTTPRedirect(self.step_url(2))

    @cherrypy.expose
    def step2(self):
        credentials = session.get(SESSION_PREFIX + "credentials")

        if not credentials:
            raise cherrypy.HTTPRedirect(self.step_url(1))

        fields = ['name', 'email']
        query = '{}{}{}{}'.format(
            'https://graph.facebook.com',
            '/me?',
            'fields=' + ','.join(fields),
            '&access_token=' + credentials['access_token']
        )

        user_data_file = urllib.urlopen(query).readline()
        user_data = json.loads(user_data_file)

        self.check_step2_errors(user_data)

        user = self.provider.process_user_data(user_data)
        app.authentication.set_user_session(user)
        del session[SESSION_PREFIX + "credentials"]

        raise cherrypy.HTTPRedirect(self.target_url)

    def check_step2_errors(self, result):

        if 'error' in result:
            if 'OAuthException' in result['error']:
                raise cherrypy.HTTPRedirect(self.step_url(1))
            else:
                msg = result.get('error_user_msg', 'Facebook user '
                                                   'authentification error')
                raise FacebookOAuthException(msg)

    def check_step1_errors(self, **kwargs):

        if "error" in kwargs:
            error_reason = kwargs.get('error_reason', 'Error')

            if error_reason == u'user_denied':
                location = Location.get_current_host()
                location.path_info = '/cms'
                raise cherrypy.HTTPRedirect(unicode(location).decode("utf-8"))
            else:
                raise FacebookOAuthException(error_reason)


CMSController.facebook_oauth = FacebookOAuthController


class FacebookOAuthException(Exception):
    pass

