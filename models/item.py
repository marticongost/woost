#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.persistence import Persistent

class Item(Persistent):

    id = schema.Integer(
        primary = True,
        auto_increment = True
    )

    type = schema.Reference(type = "magicbullet.models.ItemType")

    title = schema.String(
        max = 255,
        required = True,
        translated = True
    )

    short_desc = schema.String(
        max = 1000,
        translated = True
    )

    author = schema.Reference(type = "magicbullet.User")
    
    owner = schema.Reference(type = "magicbullet.User")

    groups = schema.Collection(
        items = "magicbullet.Group"
    )

