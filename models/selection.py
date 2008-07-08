#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class Selection(Item):
 
    query = schema.String(
        required = True,
        max = 1024
    )

