#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.persistence.entity import Entity, EntityClass

class Action(Entity):

    identifier = schema.String(
        max = 10,
        required = True,
        unique = True
    )

    title = schema.String(
        required = True,
        unique = True,
        translated = True
    )

