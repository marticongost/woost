#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from cocktail import schema
from sitebasis.models import Item, Site


class ShopOrder(Item):

    members_order = [
        "customer",
        "entries",
        "shipping_address",
        "cost"
    ]

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
        """Calculates the costs for the order.
        @rtype: dict
        """
        costs = {
            "pricing_policies": [],
            "price": {
                "cost": 0,
                "percentage": 0,
                "total": None
            },
            "shipping": 0,
            "tax": {
                "cost": 0,
                "percentage": 0
            },
            "entries": [
                {
                    "pricing_policies": [],
                    "quantity": entry.quantity,
                    "paid_quantity": entry.quantity,
                    "price": {
                        "cost": entry.product.price,
                        "percentage": 0
                    },
                    "shipping": 0,
                    "tax": {
                        "cost": 0,
                        "percentage": 0
                    }
                }
                for entry in self.entries
            ]
        }

        from sitebasis.extensions.shop import ShopExtension
        shop_ext = ShopExtension.instance

        for policies in (
            shop_ext.discounts,
            shop_ext.shipping_costs,
            shop_ext.taxes
        ):
            for pricing_policy in policies:
                matching_items = pricing_policy.select_matching_items()

                if issubclass(matching_items.type, ShopOrder):
                    if pricing_policy.applies_to(self):
                        pricing_policy.apply(self, costs)
                        costs["pricing_policies"].append(pricing_policies)
                else:
                    for entry, entry_costs in zip(self.entries, costs["entries"]):
                        if pricing_policy.applies_to(entry):
                            pricing_policy.apply(entry, costs, entry_costs)
                            entry_costs["pricing_policies"].append(pricing_policy)
        
        # Total price
        def apply_percentage(costs):
            cost = costs["cost"]
            percentage = costs["percentage"]
            if percentage:
                cost += cost * percentage / 100
            costs["total"] = cost
            return cost
        
        total_price = apply_percentage(costs["price"])

        for entry_costs in costs["entries"]:
            entry_price = apply_percentage(entry_costs["price"])
            total_price += entry_price * entry_costs["paid_quantity"]

        costs["total_price"] = total_price

        # Total taxes
        total_taxes = costs["tax"]["cost"] \
                    + total_price * cost["tax"]["percentage"] / 100
        
        for entry_costs in costs["entries"]:
            entry_price = entry_costs["total"] * entry_costs["paid_quantity"]
            entry_taxes = entry_costs["tax"]["cost"] \
                        + entry_price * entry_costs["tax"]["percentage"] / 100
            total_taxes += entry_taxes
            entry_costs["tax"]["total"] = entry_taxes

        costs["total_taxes"] = total_taxes

        # Total shipping costs
        total_shipping_costs = costs["shipping"] \
                             + sum(entry_cost["shipping"] * entry["quantity"])
        costs["total_shipping_costs"] = total_shipping_costs

        # Grand total
        costs["total"] = total_price + total_taxes + total_shipping_costs

        return costs

    def count_items(self):
        """Gets the number of purchased product units in the order.
        @rtype: int
        """
        return sum(entry.quantity for entry in self.entries)

