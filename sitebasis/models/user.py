#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import sha
from cocktail.events import event_handler
from cocktail import schema
from sitebasis.models import Item

class User(Item):
 
    edit_form = "sitebasis.views.UserForm"
    edit_controller = \
        "sitebasis.controllers.backoffice.userfieldscontroller." \
        "UserFieldsController"

    encryption = sha

    anonymous = False

    email = schema.String(
        required = True,
        unique = True,
        max = 255,
        indexed = True
        # TODO: format
    )
    
    password = schema.String(
        listable = False,
        listed_by_default = False,
        searchable = False,
        min = 8,
        edit_control = "cocktail.html.PasswordBox"
    )

    def __translate__(self, language, **kwargs):
        return self.email or Item.__translate__(self, language, **kwargs)

    @event_handler
    def handle_changing(cls, event):

        encryption = event.source.encryption

        if encryption and event.member is cls.password:
            event.value = encryption.new(event.value).digest()

    def test_password(self, password):
        """Indicates if the user's password matches the given string.
        
        @param password: An unencrypted string to tests against the user's
            encrypted password.
        @type password: str

        @return: True if the passwords match, False otherwise.
        @rtype: bool
        """
        if password:
            if self.encryption:
                return self.encryption.new(password).digest() == self.password
            else:
                return password == self.password
        else:
            return not self.password

