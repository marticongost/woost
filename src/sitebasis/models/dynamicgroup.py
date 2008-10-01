#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail import schema
from cocktail.persistence import Entity, Query
from sitebasis.models import Item

class DynamicGroup(Item):

    members_order = "title", "query"

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    query = schema.Reference(type = Query)

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Entity.__translate__(self, language, **kwargs)

