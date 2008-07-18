#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.persistence import Entity

class Item(Entity):

    title = schema.String(
        max = 255,
        required = True,
        translated = True
    )

    description = schema.String(
        max = 1000,
        translated = True
    )

    author = schema.Reference(type = "magicbullet.models.User")
    
    owner = schema.Reference(type = "magicbullet.models.User")

    groups = schema.Collection(
        items = "magicbullet.models.Group"
    )

