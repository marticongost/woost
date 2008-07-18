#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class Group(Item):
 
    members = schema.Collection(
        items = "magicbullet.models.Item"
    )

