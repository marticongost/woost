#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet import schema
from magicbullet.models import Publishable

class Event(Publishable):

    event_start = schema.DateTime()

    event_end = schema.DateTime()

    event_location = schema.String()

    body = schema.String()

