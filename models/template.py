#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class Template(Item):
 
    identifier = schema.String(
        required = True,
        unique = True,
        max = 255
    )

    types = schema.Collection(
        items = "magicbullet.ItemType"
    )
    
    items = schema.Collection(
        items = "magicbullet.Publishable"
    )

