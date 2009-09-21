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


class ShopOrder(Item):

    members_order = [
        "customer",
        "entries",
        "shipping_address",
        "cost"
    ]

    customer = schema.Reference(
        type = "sitebasis.extensions.shop.customer.Customer",
        bidirectional = True,
        required = True
    )

    entries = schema.Collection(
        items = "sitebasis.extensions.shop.shoporderentry.ShopOrderEntry",
        bidirectional = True,
        min = 1
    )

    shipping_address = schema.Reference(
        type = "sitebasis.extensions.shop.shippingaddress.ShippingAddress",
        bidirectional = True,
        required = True
    )

    cost = schema.Decimal(
        required = True,
        default = Decimal("0")
    )

    def calculate_cost(self):
        """Gets the total cost for the order.
        @rtype: decimal.Decimal
        """
        return sum(
            entry.quantity * entry.product_price
            for entry in self.entries
        )

