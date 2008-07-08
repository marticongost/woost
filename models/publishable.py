#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class Publishable(Item):

    enabled = schema.Boolean(
        required = True,
        default = True
    )

    start_date = schema.DateTime()

    end_date = schema.DateTime(
        min = lambda ctx: ctx.validable.pub_start
    )

    path = schema.String(
        max = 1024
    )

    path_is_regexp = schema.Boolean(
        required = True,
        default = False
    )
   
    controller = schema.String(max = 1024)

    template = schema.Reference(type = "magicbullet.Template")
    
    draft_source = schema.Reference(type = "magicbullet.Publishable")

    drafts = schema.Collection(items = "magicbullet.Publishable")

    attachments = schema.Collection(
        items = "magicbullet.File",
        ordered = True
    )

