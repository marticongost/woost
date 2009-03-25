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
from sitebasis.models.agent import Agent


class User(Agent):
 
    edit_form = "sitebasis.views.UserForm"
    edit_node_class = \
        "sitebasis.controllers.backoffice.usereditnode.UserEditNode"

    encryption = sha

    anonymous = False

    instantiable = True

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

    groups = schema.Collection(
        items = "sitebasis.models.Group",
        bidirectional = True
    )

    def __translate__(self, language, **kwargs):
        return self.email or Agent.__translate__(self, language, **kwargs)

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

    def get_roles(self, context):
        
        roles = [self]
        target_instance = context.get("target_instance")

        if target_instance and target_instance.owner is self:
            roles.append(
                Agent.get_instance(qname = u"sitebasis.owner")
            )
        
        if target_instance and target_instance.author is self:
            roles.append(
                Agent.get_instance(qname = u"sitebasis.author")
            )
        
        roles.extend(self.groups)
        return roles

