#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from cocktail import schema
from cocktail.translations import translations
from woost import app
from woost.models import (
    Publishable,
    with_default_template,
    with_default_controller,
    File,
    Slot
)


@with_default_template("ecommerce_product")
@with_default_controller("ecommerce_product")
class ECommerceProduct(Publishable):

    instantiable = False
    type_group = "ecommerce"

    members_order = [
        "title",
        "image",
        "description",
        "price",
        "weight",
        "purchase_model",
        "purchases"
    ]

    title = schema.String(
        indexed = True,
        normalized_index = True,
        unique = True,
        descriptive = True,
        translated = True,
        required = True,
        spellcheck = True,
        member_group = "product_data"
    )

    image = schema.Reference(
        type = File,
        related_end = schema.Collection(),
        relation_constraints = {"resource_type": "image"},
        member_group = "product_data"
    )

    description = schema.String(
        translated = True,
        edit_control = "woost.views.RichTextEditor",
        member_group = "product_data",
        spellcheck = True,
        listed_by_default = False
    )

    price = schema.Money(
        required = True,
        indexed = True,
        default = Decimal("0"),
        member_group = "product_data"
    )

    weight = schema.Decimal(
        translate_value = lambda value, language = None, **kwargs:
            "" if not value else "%s Kg" % translations(value, language),
        member_group = "product_data"
    )

    purchase_model = schema.Reference(
        class_family = "woost.extensions.ecommerce.ecommercepurchase."
                       "ECommercePurchase",
        default = schema.DynamicDefault(
            lambda: ECommerceProduct.purchase_model.class_family
        ),
        required = True,
        searchable = False,
        member_group = "product_data",
        listed_by_default = False
    )

    purchases = schema.Collection(
        items = "woost.extensions.ecommerce.ecommercepurchase."
                "ECommercePurchase",
        bidirectional = True,
        visible = False,
        member_group = "product_data"
    )

    blocks = Slot()

    def offers(self):
        website = app.website
        for pricing in website.ecommerce_pricing:
            if not pricing.hidden and pricing.applies_to(self):
                yield pricing

