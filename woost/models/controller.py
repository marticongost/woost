#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from cocktail import schema
from woost.models.item import Item


class Controller(Item):

    members_order = [
        "title",
        "python_name",
        "published_items"
    ]

    title = schema.String(
        unique = True,
        required = True,
        translated = True
    )

    python_name = schema.String(
        required = True
    )

    published_items = schema.Collection(
        items = "woost.models.Publishable",
        bidirectional = True,
        editable = False
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Item.__translate__(self, language, **kwargs)

