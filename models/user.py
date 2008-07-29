#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class User(Item):
    
    email = schema.String(
        required = True,
        unique = True,
        max = 255,
        indexed = True
        # TODO: format
    )

    authored_items = schema.Collection(
        items = "magicbullet.models.Item"
    )

    owned_items = schema.Collection(
        items = "magicbullet.models.Item"
    )

