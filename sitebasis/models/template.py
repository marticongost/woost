#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
import buffet
from cocktail import schema
from sitebasis.models import Item

class Template(Item):

    members_order = "title", "identifier", "items"

    # TODO: Allowed types

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    identifier = schema.String(
        required = True,
        unique = True,
        indexed = True,
        max = 255
    )

    engine = schema.String(
        enumeration = buffet.available_engines.keys()
    )

    items = schema.Collection(
        items = "sitebasis.models.Document",
        bidirectional = True,
        editable = False
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Item.__translate__(self, language, **kwargs)

