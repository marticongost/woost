#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.models import Publishable


class Page(Publishable):

    parent = schema.Reference(type = "magicbullet.models.Page")
 
    children = schema.Collection(
        items = "magicbullet.models.Page",
        ordered = True
    )

    hidden = schema.Boolean(
        required = True,
        default = False
    )


class StandardPage(Page):
    
    body = schema.String(translated = True)


