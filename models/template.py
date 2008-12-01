#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from sitebasis.models import Item

class Template(Item):

    members_order = "title", "identifier", "items"

    # TODO: Allowed types

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    identifier = schema.String(
        required = True,
        unique = True,
        max = 255
    )
    
    items = schema.Collection(
        items = "sitebasis.models.Document",
        bidirectional = True,
        editable = False
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Item.__translate__(self, language, **kwargs)

