#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import sha
import cherrypy
from cocktail.modeling import getter
from cocktail.persistence import datastore
from sitebasis.models import User
from sitebasis.controllers.module import Module


class AuthenticationModule(Module):

    SESSION_KEY = "user_id"

    encryption = sha
    identifier_field = User.email

    def process_request(self, request):

        params = cherrypy.request.params

        if "authenticate" in params:
            self.login(
                params.get("user"),
                params.get("password")
            )
        elif "logout" in params:
            cherrypy.session.clear()

    def _get_user(self):
        user_id = cherrypy.session.get(self.SESSION_KEY)
        return user_id and User.index[user_id] or self.anonymous_user

    def _set_user(self, user):
        cherrypy.session[self.SESSION_KEY] = user and user.id

    user = property(_get_user, _set_user, doc = """
        Gets or sets the user for the current session.
        @type: L{User<sitebasis.models.user.User>}
        """)

    @getter
    def anonymous_user(self):
        return datastore.root["anonymous_role"]

    def login(self, identifier, password):
        """
        Attemps to establish a new user session, using the given user
        credentials.

        @param identifier: An identifier matching a single user in the
            database. Matches are made against the field indicated by the
            L{identifier_field>} attribute.
        @type identifier: str

        @param password: The unencrypted password for the user.
        @type: str
        """
        identifier = identifier.strip()

        if identifier and password:
            user = self.identifier_field.index.get(identifier)

            if user \
            and self.encryption.new(password).digest() == user.password:
                self.user = user
                return user

        raise AuthenticationFailedError(identifier)


class AuthenticationFailedError(Exception):
    """An exception raised when a user authentication attempt fails."""

    def __init__(self, identifier):
        Exception.__init__(self, "Wrong user credentials")
        self.identifier = identifier

