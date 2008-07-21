#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.persistence import EntityClass
from magicbullet.models.item import Item

class AccessRule(Item):

    actor = schema.Reference(type = "magicbullet.models.Item")

    target_instance = schema.Reference(type = "magicbullet.models.Item")

    target_type = schema.Reference(type = EntityClass)

    target_ancestor = schema.Reference(type = "magicbullet.models.Page")

    action = schema.Reference(type = "magicbullet.models.Action")

    language = schema.Reference(type = "magicbullet.models.Language")

    allowed = schema.Boolean(
        required = True,
        default = True
    )

