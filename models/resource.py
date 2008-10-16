#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from cocktail.persistence import Entity
from sitebasis.models import Item

class Resource(Item):

    members_order = "title", "uri"

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    uri = schema.String(
        required = True
    )

    documents = schema.Collection(
        items = "sitebasis.models.Document",
        bidirectional = True
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Entity.__translate__(self, language, **kwargs)

