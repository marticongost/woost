#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.persistence import datastore
from magicbullet.models import allowed, AccessDeniedError
from magicbullet.controllers.module import Module


class Authorization(Module):

    def allows(self, **context):

        if "roles" not in context:
            user = self.application.authentication.user
            roles = user.get_roles(context)

            if user.anonymous:
                roles.append(datastore.root["authenticated_role"])
                
            context["roles"] = roles

        return allowed(**context)

    def restrict_access(self, **context):
        
        if not self.allows(**context):
            raise AccessDeniedError(context)
