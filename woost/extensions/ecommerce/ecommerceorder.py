#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from copy import deepcopy
from cocktail.translations import get_language, translations
from cocktail import schema
from cocktail.events import Event, event_handler
from woost import app
from woost.models import (
    Item,
    Configuration,
    User,
    ModifyMemberPermission
)
from woost.extensions.locations.location import Location
from woost.extensions.ecommerce.website import Website
from woost.extensions.ecommerce.ecommercebillingconcept \
    import ECommerceBillingConcept
from woost.extensions.payments import PaymentsExtension
from .bill import OrderBill

def _translate_amount(amount, language = None, **kwargs):
    if amount is None:
        return ""
    else:
        return translations(
            amount.quantize(Decimal("1.00")),
            language,
            **kwargs
        )

def _get_default_payment_type():
    website = app.website
    payment_types = website.ecommerce_payment_types
    if len(payment_types) == 1:
        return payment_types[0]


class ECommerceOrder(Item):

    type_group = "ecommerce"

    bill = None

    payment_types_completed_status = {
        "payment_gateway": "accepted",
        "transfer": "payment_pending",
        "cash_on_delivery": "payment_pending"
    }

    incoming = Event(doc = """
        An event triggered when a new order is received.
        """)

    completed = Event(doc = """
        An event triggered when an order is completed.
        """)

    groups_order = [
        "shipping_info",
        "billing"
    ]

    members_order = [
        "customer",
        "address",
        "town",
        "region",
        "country",
        "postal_code",
        "language",
        "status",
        "purchases",
        "payment_type",
        "total_price",
        "pricing",
        "total_shipping_costs",
        "shipping_costs",
        "total_taxes",
        "taxes",
        "total"
    ]

    website = schema.Reference(
        type = "woost.models.website.Website",
        bidirectional = True,
        required = True,
        listed_by_default = False
    )

    customer = schema.Reference(
        type = User,
        related_end = schema.Collection(),
        required = True,
        default = schema.DynamicDefault(lambda: app.user)
    )

    address = schema.String(
        member_group = "shipping_info",
        required = True,
        listed_by_default = False
    )

    town = schema.String(
        member_group = "shipping_info",
        required = True,
        listed_by_default = False
    )

    region = schema.String(
        member_group = "shipping_info",
        required = True,
        listed_by_default = False
    )

    country = schema.Reference(
        member_group = "shipping_info",
        type = Location,
        relation_constraints = [Location.location_type.equal("country")],
        default_order = "location_name",
        related_end = schema.Collection(),
        required = True,
        listed_by_default = False,
        user_filter = "cocktail.controllers.userfilter.MultipleChoiceFilter"
    )

    postal_code = schema.String(
        member_group = "shipping_info",
        required = True,
        listed_by_default = False
    )

    language = schema.String(
        required = True,
        format = "^[a-z]{2}$",
        editable = schema.READ_ONLY,
        default = schema.DynamicDefault(get_language),
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(value, language, **kwargs)
    )

    status = schema.String(
        required = True,
        indexed = True,
        enumeration = [
            "shopping",
            "payment_pending",
            "accepted",
            "failed",
            "refund"
        ],
        default = "shopping",
        text_search = False
    )

    purchases = schema.Collection(
        items = "woost.extensions.ecommerce.ecommercepurchase."
                "ECommercePurchase",
        integral = True,
        bidirectional = True,
        min = 1
    )

    payment_type = schema.String(
        member_group = "billing",
        required = True,
        enumeration = Website.ecommerce_payment_types.items.enumeration,
        default = schema.DynamicDefault(_get_default_payment_type),
        text_search = False,
        edit_control = "cocktail.html.RadioSelector",
        listed_by_default = False
    )

    total_price = schema.Money(
        member_group = "billing",
        editable = schema.READ_ONLY,
        listed_by_default = False,
        translate_value = _translate_amount
    )

    pricing = schema.Collection(
        member_group = "billing",
        items = schema.Reference(type = ECommerceBillingConcept),
        related_end = schema.Collection(
            block_delete = True
        ),
        editable = schema.READ_ONLY,
    )

    total_shipping_costs = schema.Money(
        member_group = "billing",
        editable = schema.READ_ONLY,
        listed_by_default = False,
        translate_value = _translate_amount
    )

    shipping_costs = schema.Collection(
        member_group = "billing",
        items = schema.Reference(type = ECommerceBillingConcept),
        related_end = schema.Collection(
            block_delete = True
        ),
        editable = schema.READ_ONLY,
    )

    total_taxes = schema.Money(
        member_group = "billing",
        editable = schema.READ_ONLY,
        listed_by_default = False,
        translate_value = _translate_amount
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
        editable = schema.READ_ONLY,
        translate_value = _translate_amount
    )

    def update_cost(
        self,
        bill = None,
        apply_pricing = True,
        apply_shipping_costs = True,
        apply_taxes = True
    ):
        if bill is None:
            bill = OrderBill(self)

        self.bill = bill
        self.total_price = bill.pricing.total
        self.pricing = bill.pricing.list_concepts()

        self.total_shipping_costs = bill.shipping.total
        self.shipping_costs = bill.shipping.list_concepts()

        self.total_taxes = bill.taxes.total
        self.taxes = bill.taxes.list_concepts()

        self.total = bill.total

        for purchase, purchase_bill in bill.purchases.iteritems():
            purchase.total_price = purchase_bill.pricing.total
            purchase.pricing = purchase_bill.pricing.list_concepts()
            self.pricing.extend(purchase.pricing)

            purchase.total_shipping_costs = purchase_bill.shipping.total
            purchase.shipping_costs = purchase_bill.shipping.list_concepts()
            self.shipping_costs.extend(purchase.shipping_costs)

            purchase.total_taxes = purchase_bill.taxes.total
            purchase.taxes = purchase_bill.taxes.list_concepts()
            self.taxes.extend(purchase.taxes)

            purchase.total = purchase_bill.total

    def count_units(self):
        return sum(purchase.quantity for purchase in self.purchases)

    def get_weight(self):
        return sum(purchase.get_weight() for purchase in self.purchases)

    def add_purchase(self, purchase):
        for order_purchase in self.purchases:
            if order_purchase.__class__ is purchase.__class__ \
            and order_purchase.product is purchase.product \
            and all(
                order_purchase.get(option) == purchase.get(option)
                for option in purchase.get_options()
                if option.name != "quantity"
            ):
                order_purchase.quantity += purchase.quantity
                purchase.product = None
                if purchase.is_inserted:
                    purchase.delete()
                break
        else:
            self.purchases.append(purchase)

    @classmethod
    def get_public_schema(cls):
        public_schema = schema.Schema("OrderCheckoutSummary")
        cls.get_public_adapter().export_schema(
            cls,
            public_schema
        )

        payment_type = public_schema.get_member("payment_type")
        if payment_type:
            payments = PaymentsExtension.instance
            website = app.website

            if payments.enabled and website.ecommerce_payment_gateway:

                translate_value = payment_type.translate_value

                def payment_type_translate_value(value, language = None, **kwargs):
                    if value == "payment_gateway":
                        return website.ecommerce_payment_gateway.label
                    else:
                        return translate_value(
                            value, language = language, **kwargs
                        )

                payment_type.translate_value = payment_type_translate_value

        return public_schema

    @classmethod
    def get_public_adapter(cls):
        user = app.user
        adapter = schema.Adapter()
        adapter.exclude([
            "website",
            "customer",
            "status",
            "purchases",
            "language",
            "total_price",
            "pricing",
            "total_shipping_costs",
            "shipping_costs",
            "total_taxes",
            "taxes",
            "total"
        ])
        adapter.exclude([
            member.name
            for member in cls.iter_members()
            if not member.visible
            or not member.editable
            or not issubclass(member.schema, ECommerceOrder)
            or not user.has_permission(
                ModifyMemberPermission,
                member = member
            )
        ])
        if len(app.website.ecommerce_payment_types) == 1:
            adapter.exclude(["payment_type"])
        return adapter

    @property
    def is_completed(self):
        return self.status \
        and self.status == self.payment_types_completed_status.get(
            self.payment_type
        )

    @event_handler
    def handle_changed(cls, event):

        item = event.source
        member = event.member

        if member.name == "status":

            if event.previous_value == "shopping" \
            and event.value in ("payment_pending", "accepted"):
                item.incoming()

            if item.is_completed:
                item.completed()

    def get_description_for_gateway(self):
        site_name = Configuration.instance.get_setting("site_name")
        if site_name:
            return translations(
                "woost.extensions.ecommerceorder.ECommerceOrder.description_for_gateway",
                site_name
            )
        else:
            return translations(self)

