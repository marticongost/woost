#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail import schema
from sitebasis.models import Item


class ProductCategory(Item):

    members_order = [
        "title",
        "parent",
        "children",
        "products"
    ]

    title = schema.String(
        required = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    parent = schema.Reference(
        type = "sitebasis.extensions.shop.category.Category",
        bidirectional = True
    )

    children = schema.Collection(
        items = "sitebasis.extensions.shop.category.Category",
        bidirectional = True
    )

    products = schema.Collection(
        items = "sitebasis.extensions.shop.product.Product",
        bidirectional = True
    )

    def __translate__(self, language, **kwargs):
        return (
            self.draft_source is None
            and self.get("title", language)
        ) or Item.__translate__(self, language, **kwargs)

