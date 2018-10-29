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
from woost import app
from woost.models import (
    Item,
    ModifyMemberPermission
)
from woost.extensions.ecommerce.ecommercebillingconcept \
    import ECommerceBillingConcept
from .bill import PurchaseBill


class ECommercePurchase(Item):

    visible_from_root = False

    members_order = [
        "order",
        "product",
        "quantity",
        "total_price",
        "pricing",
        "total_shipping_costs",
        "shipping_costs",
        "total_taxes",
        "taxes",
        "total"
    ]

    order = schema.Reference(
        type = "woost.extensions.ecommerce.ecommerceorder.ECommerceOrder",
        bidirectional = True,
        required = True
    )

    product = schema.Reference(
        type = "woost.extensions.ecommerce.ecommerceproduct.ECommerceProduct",
        bidirectional = True,
        required = True
    )

    quantity = schema.Integer(
        required = True,
        min = 1,
        default = 1
    )

    total_price = schema.Money(
        member_group = "billing",
        editable = schema.READ_ONLY,
        listed_by_default = False
    )

    pricing = schema.Collection(
        member_group = "billing",
        items = schema.Reference(type = ECommerceBillingConcept),
        related_end = schema.Collection(
            block_delete = True
        ),
        editable = schema.READ_ONLY
    )

    total_shipping_costs = schema.Money(
        member_group = "billing",
        editable = schema.READ_ONLY,
        listed_by_default = False
    )

    shipping_costs = schema.Collection(
        member_group = "billing",
        items = schema.Reference(type = ECommerceBillingConcept),
        related_end = schema.Collection(
            block_delete = True
        ),
        editable = schema.READ_ONLY
    )

    total_taxes = schema.Money(
        member_group = "billing",
        editable = schema.READ_ONLY,
        listed_by_default = False
    )

    taxes = schema.Collection(
        member_group = "billing",
        items = schema.Reference(type = ECommerceBillingConcept),
        related_end = schema.Collection(
            block_delete = True
        ),
        editable = schema.READ_ONLY
    )

    total = schema.Money(
        member_group = "billing",
        editable = schema.READ_ONLY
    )

    def get_unit_price(self):
        return self.product.price

    def get_weight(self):
        if self.product is None or self.product.weight is None:
            return 0
        else:
            return self.quantity * self.product.weight

    @classmethod
    def get_options(cls):
        for member in cls.iter_members():
            if (
                member is not cls.product
                and member is not cls.order
                and member.visible
                and member.editable == schema.EDITABLE
                and issubclass(member.schema, ECommercePurchase)
                and app.user.has_permission(
                    ModifyMemberPermission,
                    member = member
                )
            ):
                yield member


@translations.instances_of(ECommercePurchase)
def translate_ecommerce_purchase(self, **kwargs):

    if not self.quantity or not self.product:
        return None

    desc = u"%d x %s" % (
        self.quantity,
        translations(self.product)
    )

    options = []
    for member in self.get_options():
        if member is ECommercePurchase.quantity:
            continue
        options.append("%s: %s" % (
            translations(member),
            member.translate_value(self.get(member))
        ))

    if options:
        desc += u" (%s)" % u", ".join(options)

    return desc

