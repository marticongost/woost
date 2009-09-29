#-*- coding: utf-8 -*-
"""
Provides a variety of models to implement customized offers, discounts, and
other specialized pricing policies for a shop.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail import schema
from cocktail.controllers.usercollection import UserCollection
from sitebasis.models import Item, Site
from sitebasis.extensions.shop.shoporder import ShopOrder
from sitebasis.extensions.shop.shoporderentry import ShopOrderEntry


class PricingPolicy(Item):

    visible_from_root = False
    integral = True
    instantiable = False

    members_order = [
        "title",
        "enabled",
        "start_date",
        "end_date"
    ]

    title = schema.String()
    
    enabled = schema.Boolean(
        required = True,
        default = True
    )

    start_date = schema.DateTime(
        indexed = True
    )

    end_date = schema.DateTime(
        indexed = True,
        min = start_date
    )
     
    matching_items = schema.Mapping()

    # TODO: Validate that issubclass(matching_items["type"], (ShopOrder, ShopOrderEntry))

    def is_current(self):
        return (self.start_date is None or self.start_date <= datetime.now()) \
           and (self.end_date is None or self.end_date > datetime.now())

    def select_matching_items(self, *args, **kwargs):
        user_collection = UserCollection(Item)
        user_collection.allow_paging = False
        user_collection.allow_member_selection = False
        user_collection.allow_language_selection = False
        user_collection.params.source = self.matching_items.get
        #user_collection.available_languages = Language.codes # <- required?
        return user_collection.subset
    
    def match_item(self, item):

        if self.matching_items:
            for filter in self.select_matching_items().filters:
                if not filter.eval(item):
                    return False
        
        return True

    def applies_to(self, item):
        return self.enabled and self.is_current() and self.match_item(item)

    def apply(self, item, costs):
        pass


class Discount(PricingPolicy):

    highlighted = schema.Boolean(
        required = True,
        default = True
    )


class PriceOverride(Discount):

    instantiable = True

    price = schema.Decimal(
        required = True
    )

    def apply(self, item, costs):
        costs["price"]["cost"] = self.price


class RelativeDiscount(Discount):

    instantiable = True
    
    amount = schema.Decimal(
        required = True
    )
    
    def apply(self, item, costs):
        costs["price"]["cost"] -= self.amount


class PercentageDiscount(Discount):

    instantiable = True

    percentage = schema.Decimal(
        required = True
    )

    def apply(self, item, costs):
        costs["price"]["percentage"] -= self.percentage


class FreeUnitsDiscount(Discount):

    instantiable = True
    members_order = ["paid_units", "free_units", "repeated"]

    members_order = [
        "paid_units",
        "free_units",
        "repeated"
    ]
    
    paid_units = schema.Integer(
        required = True,
        min = 0
    )

    free_units = schema.Integer(
        required = True,
        min = 1
    )

    repeated = schema.Boolean(
        required = True,
        default = True
    )

    def apply(self, item, costs):

        paid = self.paid_units
        free = self.free_units
        quantity = costs["paid_quantity"]
        
        if self.repeated:
            quantity -= (quantity / (paid + free)) * free
        elif quantity > paid:
            quantity = max(paid, quantity - free)

        costs["paid_quantity"] = quantity


class ShippingCost(PricingPolicy):
    pass   


class ShippingCostOverride(ShippingCost):
    
    instantiable = True
    
    cost = schema.Decimal(
        required = True
    )
    
    def apply(self, item, costs):
        costs["shipping"] = self.cost


class CumulativeShippingCost(ShippingCost):

    instantiable = True

    cost = schema.Decimal(
        required = True
    )

    def apply(self, item, costs):
        costs["shipping"] += self.cost


class Tax(PricingPolicy):
    pass


class CumulativeTax(Tax):

    instantiable = True

    cost = schema.Decimal(
        required = True
    )

    def apply(self, item, costs):
        costs["tax"]["cost"] += self.cost


class PercentageTax(Tax):

    instantiable = True
        
    percentage = schema.Decimal(
        required = True
    )

    def apply(self, item, costs):
        costs["tax"]["percentage"] += self.percentage

