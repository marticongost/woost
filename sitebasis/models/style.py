#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail import schema
from cocktail.modeling import getter
from sitebasis.models import Item


class Style(Item):

    members_order = "title", "declarations"

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    declarations = schema.String(
        required = True
    )
    
    admin_declarations = schema.String(
        required = False
    )
    
    @getter
    def class_name(self):
        return "sitebasis_style_%d" % self.id

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Item.__translate__(self, language, **kwargs)

