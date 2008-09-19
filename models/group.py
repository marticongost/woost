#-*- coding: utf-8 -*-
"""

@author:		Mart� Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.persistence import Entity
from magicbullet.models import Item

class Group(Item):
 
    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    group_members = schema.Collection(
        items = "magicbullet.models.Item"
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Entity.__translate__(self, language, **kwargs)

