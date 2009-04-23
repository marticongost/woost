#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail import schema
from sitebasis.models.document import Document

class News(Document):

    members_order = "summary", "body"

    summary = schema.String(
        edit_control = "sitebasis.views.RichTextEditor",
        listed_by_default = False
    )

    body = schema.String(
        edit_control = "sitebasis.views.RichTextEditor",
        listed_by_default = False
    )

