#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from sitebasis.models import Extension

translations.define("ShopExtension",
    ca = u"Botiga",
    es = u"Tienda",
    en = u"Shop"
)

translations.define("ShopExtension-plural",
    ca = u"Botigues",
    es = u"Tiendas",
    en = u"Shops"
)


class ShopExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Proporciona els elements necessaris per implementar una botiga
            electrònica.""",
            "ca"
        )
        self.set("description",            
            u"""Proporciona los elementos necesarios para implementar una
            tienda electrónica.""",
            "es"
        )
        self.set("description",
            u"""Supplies the building blocks required to implement an online
            shop.""",
            "en"
        )

    @event_handler
    def handle_loading(cls, event):

        from sitebasis.extensions import shop
        from sitebasis.extensions.shop import (
            strings,
            product,
            productcategory,
            shoporder,
            shoporderentry,
            pricing,
            basket
        )

        for module, keys in (
            (shop.product, ("Product",)),
            (shop.productcategory, ("ProductCategory",)),
            (shop.shoporder, ("ShopOrder",)),
            (shop.shoporderentry, ("ShopOrderEntry",)),
            (shop.pricing, (
                "PricingPolicy",
                "Discount",
                "PriceOverride",
                "RelativeDiscount",
                "PercentageDiscount",
                "FreeUnitsDiscount",
                "ShippingCost",
                "ShippingCostOverride",
                "CumulativeShippingCost",
                "Tax",
                "CumulativeTax",
                "PercentageTax"
            )),
            (shop.basket, ("Basket",))
        ):
            for key in keys:
                setattr(shop, key, getattr(module, key))

        ShopExtension.add_member(
            schema.Collection("discounts",
                items = schema.Reference(type = pricing.Discount),
                related_end = schema.Reference()
            )
        )

        ShopExtension.add_member(
            schema.Collection("shipping_costs",
                items = schema.Reference(type = pricing.ShippingCost),
                related_end = schema.Reference()
            )
        )

        ShopExtension.add_member(
            schema.Collection("taxes",
                items = schema.Reference(type = pricing.Tax),
                related_end = schema.Reference()
            )
        )

