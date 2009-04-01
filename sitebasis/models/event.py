#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail import schema
from sitebasis.models.document import Document

class Event(Document):

    members_order = "event_start", "event_end", "event_location", "body"

    event_start = schema.DateTime()

    event_end = schema.DateTime()

    event_location = schema.String(
        edit_control = "cocktail.html.TextArea"
    )

    body = schema.String(
        edit_control = "sitebasis.views.RichTextEditor"
    )

