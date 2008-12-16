#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2008
"""
from cocktail import schema
from sitebasis.models import Item

class Role(Item):

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    anonymous = False

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Item.__translate__(self, language, **kwargs)

