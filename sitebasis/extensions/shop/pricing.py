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
from sitebasis.models import Item, Site
from sitebasis.extensions.shop.shoporder import ShopOrder
from sitebasis.extensions.shop.shoporderentry import ShopOrderEntry


class Pricing(Item):

    visible_from_root = False
    integral = True
    instantiable = False

    members_order = [
        "title",
        "enabled",
        "start_date",
        "end_date",
        "highlighted"
    ]

    concept = None

    site = schema.Reference(
        visible = False,
        type = Site,
        related_end = schema.Collection("pricing_policies")
    )

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

    highlighted = schema.Boolean(
        required = True
    )
 
    def is_current(self):
        return (self.start_date is None or self.start_date <= datetime.now()) \
           and (self.end_date is None or self.end_date > datetime.now())


def _display_tax_scope(parent, obj, member):
    value = schema.get(obj, member)
    if value is None:
        return None
    else:
        return translations(
            "sitebasis.extensions.shop tax_scope "
            + schema.get(obj, member)
        )

def _display_modifier_type(parent, obj, member):
    value = schema.get(obj, member)
    if value is None:
        return None
    else:
        return translations(
            "sitebasis.extensions.shop price_modifier_type "
            + schema.get(obj, member)
        )

def _apply_modifier(modifier, modifier_type, values):
    if modifier_type == "absolute":
        values["cost"] = modifier
    elif modifier_type == "relative":
        values["cost"] += modifier
    elif modifier_type == "percentage":
        values["percentage"] += modifier

# Order pricing
#------------------------------------------------------------------------------

class OrderPricing(Pricing):

    instantiable = False

    matching_orders = schema.Mapping()

    def is_available(self, order):
        return Pricing.is_available(self, order) \
           and self.match_order(order)

    def select_matching_orders(self, *args, **kwargs):
        user_collection = UserCollection(ShopOrder)
        user_collection.allow_paging = False
        user_collection.allow_member_selection = False
        user_collection.allow_language_selection = False
        user_collection.params.source = self.matching_items.get
        #user_collection.available_languages = Language.codes # <- required?
        return user_collection.subset
    
    def match_order(self, order):

        if self.matching_orders:
            for filter in self.select_matching_orders().filters:
                if not filter.eval(order):
                    return False
        
        return True

    def apply(self, order, values):
        pass


class OrderPrice(OrderPricing):
    
    concept = "price"

    instantiable = True
    members_order = ["modifier", "modifier_type"]

    modifier = schema.Decimal(
        required = True
    )

    modifier_type = schema.String(
        enumeration = ["absolute", "relative", "percentage"],
        required = True,
        default = "absolute",
        display = _display_modifier_type            
    )

    def apply(self, order, values):
        _apply_modifier(self.modifier, self.modifier_type, values)


class OrderShippingCost(OrderPricing):

    concept = "shipping"

    instantiable = True
    members_order = ["modifier", "modifier_type"]

    modifier = schema.Decimal(
        required = True
    )

    modifier_type = schema.String(
        enumeration = ["absolute", "relative", "percentage"],
        required = True,
        default = "absolute",
        display = _display_modifier_type
    )

    def apply(self, order, values):
        _apply_modifier(self.modifier, self.modifier_type, values)


class OrderTax(OrderPricing):

    concept = "tax"

    instantiable = True
    members_order = [
        "tax_scope",
        "modifier",
        "modifier_type"
    ]

    tax_scope = schema.String(
        enumeration = ["price", "shipping", "total"],
        required = True,
        default = "total",
        display = _display_tax_scope
    )

    modifier = schema.Decimal(
        required = True
    )

    modifier_type = schema.String(
        enumeration = ["relative", "percentage"],
        required = True,
        default = "percentage",
        display = _display_modifier_type
    )

    def apply(self, order, values):
        _apply_modifier(self.modifier, self.modifier_type, values)


# Entry pricing
#------------------------------------------------------------------------------

class EntryPricing(Pricing):

    instantiable = False

    matching_entries = schema.Mapping()
   
    def is_available(self, entry):
        return Pricing.is_available(self) and self.match_entry(entry)

    def select_matching_entries(self, *args, **kwargs):
        user_collection = UserCollection(ShopOrderEntry)
        user_collection.allow_paging = False
        user_collection.allow_member_selection = False
        user_collection.allow_language_selection = False
        user_collection.params.source = self.matching_items.get
        #user_collection.available_languages = Language.codes # <- required?
        return user_collection.subset
    
    def match_entry(self, entry):

        if self.matching_entries:
            for filter in self.select_matching_entries().filters:
                if not filter.eval(entry):
                    return False
        
        return True

    def apply(self, entry, values):
        pass 


class EntryPrice(EntryPricing):
    
    concept = "price"

    instantiable = True
    members_order = ["modifier", "modifier_type"]

    modifier = schema.Decimal(
        required = True
    )
    
    modifier_type = schema.String(
        enumeration = ["absolute", "relative", "percentage"],
        required = True,
        default = "absolute",
        display = _display_modifier_type
    )

    def apply(self, entry, values):
        _apply_modifier(self.modifier, self.modifier_type, values)


class EntryFreeUnits(EntryPricing):

    concept = "price"

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

    def apply(self, entry, values):
                
        paid = self.paid_units
        free = self.free_units
        quantity = values["paid_quantity"]

        quantity, r = divmod(quantity, paid + free)
        
        if self.repeated:
            quantity -= (q * free + max(0, r - paid))
        elif quantity > paid:
            quantity = max(paid, quantity - free)

        values["paid_quantity"] = max(0, quantity)


class EntryShippingCost(EntryPricing):

    concept = "shipping"

    instantiable = True
    members_order = ["modifier", "modifier_type"]

    modifier = schema.Decimal(
        required = True
    )

    modifier_type = schema.String(
        enumeration = ["absolute", "relative", "percentage"],
        required = True,
        default = "absolute",
        display = _display_modifier_type
    )

    def apply(self, entry, values):
        _apply_modifier(self.modifier, self.modifier_type, values)


class EntryTax(EntryPricing):

    concept = "tax"

    instantiable = True
    members_order = [
        "tax_scope",
        "modifier",
        "modifier_type"
    ]

    tax_scope = schema.String(
        enumeration = ["price", "shipping", "total"],
        required = True,
        default = "total",
        display = _display_tax_scope
    )

    modifier = schema.Decimal(
        required = True
    )

    modifier_type = schema.String(
        enumeration = ["relative", "percentage"],
        required = True,
        default = "percentage",
        display = _display_modifier_type
    )

    def apply(self, entry, values):
        _apply_modifier(self.modifier, self.modifier_type, values)

