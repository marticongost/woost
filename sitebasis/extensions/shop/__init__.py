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
            (product, ("Product",)),
            (productcategory, ("ProductCategory",)),
            (shoporder, ("ShopOrder",)),
            (shoporderentry, ("ShopOrderEntry",)),
            (pricing, (
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
            (basket, ("Basket",))
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

        from tpv import (
            Currency,
            Payment,
            PaymentItem,
            PaymentGateway,
            PaymentNotFoundError
        )
        from sitebasis.extensions.payments import PaymentsExtension

        payments_ext = PaymentsExtension.instance
            
        def get_payment(payment_id):

            order = shoporder.ShopOrder.get_instance(int(payment_id))

            if order is None:
                raise PaymentNotFoundError(payment_id)
            
            costs = order.calculate_cost()
            payment = Payment()
            payment.id = order.id
            payment.amount = costs["total"]
            payment.shop_order = order
            payment.currency = Currency(payments_ext.payment_gateway.currency)
            
            for entry, entry_costs in zip(order.entries, costs["entries"]):
                payment.add(PaymentItem(
                    reference = str(entry.product.id),
                    description = translations(entry.product),
                    quantity = entry.quantity,
                    price = entry_costs["price"]["total"]
                ))

            return payment

        PaymentGateway.get_payment = get_payment

