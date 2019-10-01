#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from typing import Dict, Union
from string import ascii_letters, digits
from datetime import datetime, timedelta

import cherrypy
from cocktail.translations import translations
from cocktail.stringutils import random_string
from cocktail.schema import ErrorList
from cocktail.controllers import (
    session,
    get_request_url_builder,
    redirect
)
from cocktail.persistence import PersistentMapping

from woost import app
from woost.models import User

translations.load_bundle("woost.authentication.package")


class AuthenticationScheme(object):

    SESSION_KEY = "user_id"
    AUTH_TOKEN_HEADER = "X-Woost-Auth"
    AUTH_STR_LENGTH = 40
    AUTH_STR_CHARS = ascii_letters + digits

    identifier_field = User.email

    def process_request(self):

        app.user = (
            self.get_user_from_session()
            or self.anonymous_user
        )

        try:
            self.process_auth()
        except AuthenticationFailedError as e:
            authentication_errors = ErrorList()
            authentication_errors.add(e)
            cherrypy.request.authentication_errors = authentication_errors
            raise
        self.process_logout()

    def process_auth(self):
        self.process_auth_token()
        self.process_login()

    def process_auth_token(self):
        """Authenticates the current request using an authentication token
        included in an HTTP header.

        The method looks for an X-Woost-Auth header containing an
        authentication token previously generated by `create_auth_token`. If
        the header exists, its value is processed by `parse_auth_token`, and
        the resulting user is set as the active user for the current request
        only (it doesn't start a user session).

        If the active request doesn't contain the authentication header the
        method will do nothing.

        :raise `AuthenticationFailedError`: Raised if the token is badly
            formatted, doesn't exist, has been revoked or has expired.
        """
        auth_token = cherrypy.request.headers.get(self.AUTH_TOKEN_HEADER)
        if auth_token:
            app.user = self.parse_auth_token(auth_token)

    def parse_auth_token(self, token: str) -> User:
        """Resolve an authentication token, obtaining its matching user.

        Evaluates an authentication token previously produced by
        `create_auth_token`, and returns the user it is assigned to.

        :return: The user matching the given token.

        :raise `AuthenticationFailedError`: Raised if the token is badly
            formatted, doesn't exist, has been revoked or has expired.
        """
        try:
            user_id, auth_str = token.split("-", 1)
            user_id = int(user_id)
        except ValueError:
            raise AuthenticationFailedError(token) from None

        user = User.get_instance(user_id)
        if user is None or not user._auth_tokens:
            raise AuthenticationFailedError(token)

        try:
            expiration = user._auth_tokens[auth_str]
        except KeyError:
            raise AuthenticationFailedError(token) from None

        if expiration is not None and datetime.now() >= expiration:
            raise AuthenticationFailedError(token)

        return user

    def create_auth_token(
            self,
            user: User,
            expiration: Union[timedelta, datetime] = None) -> str:
        """Creates an authentication token that can be used to authenticate
        future HTTP requests to the CMS.

        The resulting token should be added to HTTP requests using an
        X-Woost-Auth header. The CMS will use `process_auth_token` to resolve it
        and authenticate the request.

        Tokens can expire (by setting the `expiration` parameter) or be
        explicitly revoked (by calling `revoke_auth_token`).

        :param user: The user to generate the token for. Requests including the
            token in the appropiate HTTP header will be authenticated as the
            given user.

        :param expiration: An optional expiration date for the token. Can be
            given as a datetime (signaling the moment when the token will
            expire) or as a timedelta (which will be added to the current time
            to obtain the datetime for the expiration).
        """
        assert user is not None
        assert user.is_inserted
        assert not user.anonymous

        tokens = user._auth_tokens
        if tokens is None:
            tokens = PersistentMapping()
            user._auth_tokens = tokens

        if isinstance(expiration, timedelta):
            expiration = datetime.now() + expiration

        token = random_string(self.AUTH_STR_LENGTH, self.AUTH_STR_CHARS)
        tokens[token] = expiration
        return f"{user.id}-{token}"

    def revoke_auth_token(self, token: str) -> bool:
        """Revokes the given authentication token.

        :param token: An authentication token previously generated by
            `create_auth_token`.

        :return: True if the token was successfully revoked, False if it was
            malformed or didn't match any existing token.
        """
        try:
            user_id, auth_str = token.split("-", 1)
            user_id = int(user_id)
        except ValueError:
            pass
        else:
            user = User.get_instance(user_id)
            if user and user._auth_tokens and user._auth_tokens.pop(auth_str):
                return True

        return False

    def process_login(self):
        params = cherrypy.request.params
        if "authenticate" in params:
            self.login(
                params.get("user"),
                params.get("password")
            )

            # Request the current location again, with all authentication
            # parameters stripped
            url_builder = get_request_url_builder()
            url_builder.query.pop("user", None)
            url_builder.query.pop("password", None)
            url_builder.query.pop("authenticate", None)
            redirect(url_builder)

    def process_logout(self):
        if "logout" in cherrypy.request.params:
            self.logout()

    @property
    def anonymous_user(self):
        return User.get_instance(qname = "woost.anonymous_user")

    def get_user_from_session(self):
        session_user_id = session.get(self.SESSION_KEY)
        if session_user_id:
            return User.get_instance(session_user_id)

    def set_user_session(self, user):
        session[self.SESSION_KEY] = user.id
        app.user = user

    def login(self, identifier, password):
        """Attempts to establish a new user session, using the given user
        credentials.

        @param identifier: An identifier matching a single user in the
            database. Matches are made against the field indicated by the
            L{identifier_field>} attribute.
        @type identifier: str

        @param password: The unencrypted password for the user.
        @type: str

        @return: The authenticated user.
        @rtype: L{User<woost.models.user.User>}

        @raise L{AuthenticationFailedError}: Raised if the provided user
            credentials are invalid.
        """
        identifier = identifier.strip()

        if identifier and password:
            params = {self.identifier_field.name: identifier}
            user = User.get_instance(**params)

            if user and self.can_login(user) and user.test_password(password):
                self.set_user_session(user)
                return user

        raise AuthenticationFailedError(identifier)

    def can_login(self, user):
        """Indicates if the given user is allowed to begin an authenticated
        session.

        Implementations can override this method to disable log in for users
        fulfilling specific criteria. If a disabled user attempts to log in,
        the authentication scheme will raise an `AuthenticationFailedError`
        exception.

        :param user: The user to validate.
        :type user: `woost.models.user.User`

        :return: A boolean value indicating if the user is allowed to log in.
        """
        return user.enabled

    def logout(self):
        """Ends the current user session."""
        session.delete()
        app.user = self.anonymous_user


class AuthenticationFailedError(Exception):
    """An exception raised when a user authentication attempt fails."""

    def __init__(self, identifier):
        Exception.__init__(self, "Wrong user credentials")
        self.identifier = identifier

