#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import date
from cocktail import schema
from .document import Document
from .file import File
from .slot import Slot
from .defaulttemplate import with_default_template


@with_default_template("news")
class News(Document):

    members_order = [
        "news_date",
        "image",
        "blocks"
    ]

    news_date = schema.Date(
        required = True,
        indexed = True,
        default = schema.DynamicDefault(date.today),
        member_group = "content"
    )

    image = schema.Reference(
        type = File,
        related_end = schema.Collection(),
        relation_constraints = {"resource_type": "image"},
        member_group = "content"
    )

    blocks = Slot()

