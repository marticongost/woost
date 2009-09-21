#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from cocktail import schema
from sitebasis.models import Item


class Product(Item):

    members_order = [
        "product_name",
        "price",
        "description",
        "categories",
        "entries"
    ]

    product_name = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    price = schema.Decimal(
        required = True,
        default = Decimal("0")
    )
    
    description = schema.String(
        edit_control = "sitebasis.views.RichTextEditor"
    )

    categories = schema.Collection(
        items = "sitebasis.extensions.shop.productcategory.ProductCategory",
        bidirectional = True
    )

    entries = schema.Collection(
        items = "sitebasis.extensions.shop.shoporderentry.ShopOrderEntry",
        bidirectional = True,
        visible = False,
        block_delete = True
    )

    def __translate__(self, language, **kwargs):
        return (
            self.draft_source is None
            and self.get("product_name", language)
        ) or Item.__translate__(self, language, **kwargs)

