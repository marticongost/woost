#-*- coding: utf-8 -*-
"""

@author:		Mart� Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class Page(Item):

    parent = schema.Reference(type = "magicbullet.Page")
 
    children = schema.Collection(
        items = "magicbullet.Page",
        ordered = True
    )

    hidden = schema.Boolean(
        required = True,
        default = False
    )

    resources = schema.Collection(
        items = "magicbullet.Resource",
        ordered = True
    )

