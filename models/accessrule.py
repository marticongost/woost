#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class AccessRule(Item):

    subject = schema.Reference(type = "magicbullet.Item")

    target_instance = schema.Reference(type = "magicbullet.Item")

    target_type = schema.Reference(type = "magicbullet.ItemType")

    target_ancestor = schema.Reference(type = "magicbullet.ItemType")

    action = schema.Reference(type = "magicbullet.Action")

    language = schema.Reference(type = "magicbullet.Language")

    allowed = schema.Boolean(
        required = True,
        default = True
    )

    order = schema.Integer(
        required = True,
        unique = True
    )

