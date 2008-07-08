#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.persistence import Persistent

class ItemType(Persistent):

    id = schema.String(
        primary = True,
        max = 255
    )

    title = schema.String(
        max = 255,
        required = True,
        translated = True
    )

    actions = schema.Collection(items = "magicbullet.Actions")

    templates = schema.Collection(items = "magicbullet.Template")

