#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.persistence import datastore
from sitebasis.models import allowed, AccessDeniedError
from sitebasis.controllers.module import Module


class AuthorizationModule(Module):

    def allows(self, **context):

        if "user" not in context:
            context["user"] = self.application.authentication.user
        
        return allowed(**context)

    def restrict_access(self, **context):
        
        if not self.allows(**context):
            raise AccessDeniedError(context)
