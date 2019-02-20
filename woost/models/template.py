#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from .item import Item
from .theme import Theme
from cocktail.html import templates


class Template(Item):

    type_group = "customization"
    admin_show_descriptions = False

    members_order = [
        "title",
        "identifier",
        "theme",
        "documents"
    ]

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True,
        spellcheck = True
    )

    identifier = schema.String(
        required = True,
        text_search = False
    )

    theme = schema.Reference(
        type = Theme,
        related_end = schema.Collection(),
        listed_by_default = False
    )

    documents = schema.Collection(
        items = "woost.models.Document",
        bidirectional = True,
        editable = schema.NOT_EDITABLE,
        visible = False
    )

    view_initialization = schema.CodeBlock(
        language = "python"
    )

    def create_view(self):
        view = templates.new(self.identifier)
        if self.view_initialization:
            self.__class__.view_initialization.execute(self, {
                "view": view,
                "template": self
            })
        return view

