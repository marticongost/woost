#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models import Publishable

class News(Publishable):

    members_order = "summary", "body"

    summary = schema.String()

    body = schema.String()

