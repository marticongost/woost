#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.persistence import Entity, EntityClass
from magicbullet.models import Item

class Template(Item):

    members_order = "title", "identifier", "types", "items"

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

    types = schema.Collection(
        items = EntityClass
    )
    
    items = schema.Collection(
        items = "magicbullet.models.Document",
        bidirectional = True
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Entity.__translate__(self, language, **kwargs)

