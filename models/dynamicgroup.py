#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models import Item
from magicbullet.persistence import Query

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
        return self.get("title", language)

