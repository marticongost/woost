#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail import schema
from cocktail.persistence import Entity
from sitebasis.models import Item


class Style(Item):

    members_order = "title", "declarations"

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    declarations = schema.String(
        required = True
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Entity.__translate__(self, language, **kwargs)

