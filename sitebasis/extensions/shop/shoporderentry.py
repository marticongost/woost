#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from cocktail.translations import translations
from cocktail import schema
from sitebasis.models import Item


class ShopOrderEntry(Item):

    integral = True
    listed_from_root = False

    members_order = [
        "shop_order",
        "product",
        "quantity"
    ]

    shop_order = schema.Reference(
        type = "sitebasis.extensions.shop.shoporder.ShopOrder",
        bidirectional = True,
        required = True
    )

    product = schema.Reference(
        type = "sitebasis.extensions.shop.product.Product",
        bidirectional = True,
        required = True
    )

    quantity = schema.Integer(
        required = True,
        min = 1
    )

    def __translate__(self, language, **kwargs):
        if self.draft_source is not None:
            return Item.__translate__(self, language, **kwargs)

        return "%s (%d)" % (
            translations(self.product, language),
            self.quantity
        )

