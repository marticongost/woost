#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from sitebasis.models import Item

class Group(Item):
 
    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    group_members = schema.Collection(
        items = "sitebasis.models.Item",
        bidirectional = True
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Item.__translate__(self, language, **kwargs)

