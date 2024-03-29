#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from cocktail import schema
from .item import Item


class Controller(Item):

    type_group = "customization"

    members_order = [
        "title",
        "python_name",
        "published_items"
    ]

    title = schema.String(
        unique = True,
        required = True,
        descriptive = True,
        translated = True
    )

    python_name = schema.String(
        required = True,
        text_search = False
    )

    published_items = schema.Collection(
        items = "woost.models.Publishable",
        bidirectional = True,
        editable = False,
        synchronizable = False,
        visible_in_reference_list = False
    )

