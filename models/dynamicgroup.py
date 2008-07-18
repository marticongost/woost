#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models import Item
from magicbullet.persistence import Query

class DynamicGroup(Item):

    query = schema.Reference(type = Query)

