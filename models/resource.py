#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class Resource(Item):

    members_order = "title", "html"

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    html = schema.String(
        required = True
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language)

