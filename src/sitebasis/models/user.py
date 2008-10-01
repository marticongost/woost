#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail import schema
from sitebasis.models import Item

class User(Item):
 
    anonymous = False

    email = schema.String(
        required = True,
        unique = True,
        max = 255,
        indexed = True
        # TODO: format
    )

    def __translate__(self, language, **kwargs):
        return self.email

