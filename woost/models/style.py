#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail import schema
from cocktail.modeling import getter
from woost.models import Item


class Style(Item):

    members_order = [
        "title",
        "custom_class_name",
        "declarations",
        "admin_declarations"
    ]

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True
    )

    custom_class_name = schema.String(
        indexed = True,
        unique = True,
        normalized_index = False
    )

    declarations = schema.String(
        required = True,
        text_search = False,
        edit_control = "cocktail.html.TextArea"
    )
    
    admin_declarations = schema.String(
        text_search = False,
        edit_control = "cocktail.html.TextArea"
    )

    @property
    def class_name(self):
        return self.custom_class_name or ("woost_style_%d" % self.id)

