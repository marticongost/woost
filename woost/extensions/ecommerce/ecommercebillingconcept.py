#-*- coding: utf-8 -*-
"""Provides a variety of models to implement customizable discounts, taxes and
shipping costs.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from decimal import Decimal
from datetime import datetime
from cocktail.modeling import abstractmethod
from cocktail.translations import translations
from cocktail import schema
from woost.models import Item, Role
from woost.extensions.locations.location import Location
from woost.extensions.ecommerce.ecommerceproduct import ECommerceProduct

override_regexp = re.compile(r"^=\s*((-|\+)?\d+(.\d+)?)$")
add_regexp = re.compile(r"^((-|\+)?\d+(.\d+)?)$")
override_percentage_regexp = re.compile(r"^=\s*((-|\+)?\d+(\.\d+)?)%$")
add_percentage_regexp = re.compile(r"^((-|\+)?\d+(\.\d+)?)%$")
free_units_regexp = re.compile(r"^\d\s*x\s*\d?$")


class ECommerceBillingConcept(Item):

    members_order = [
        "title",
        "enabled",
        "start_date",
        "end_date",
        "hidden",
        "scope",
        "eligible_countries",
        "eligible_products",
        "eligible_roles",
        "condition",
        "implementation"
    ]

    visible_from_root = False

    title = schema.String(
        translated = True,
        descriptive = True,
        required = True,
        spellcheck = True
    )

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

    hidden = schema.Boolean(
        default = False,
        required = True
    )

    scope = schema.String(
        required = True,
        enumeration = ["order", "purchase"],
        default = "order",
        edit_control = "cocktail.html.RadioSelector"
    )

    condition = schema.CodeBlock(
        language = "python"
    )

    eligible_countries = schema.Collection(
        items = schema.Reference(
            type = Location,
            relation_constraints = [Location.location_type.equal("country")]
        ),
        related_end = schema.Collection()
    )

    eligible_products = schema.Collection(
        items = schema.Reference(type = ECommerceProduct),
        related_end = schema.Collection()
    )

    eligible_roles = schema.Collection(
        items = schema.Reference(type = Role),
        related_end = schema.Collection()
    )

    implementation = schema.CodeBlock(
        language = "python"
    )

    def is_current(self):
        return (self.start_date is None or self.start_date <= datetime.now()) \
           and (self.end_date is None or self.end_date > datetime.now())

    def applies_to(self, target):

        from .bill import Bill
        from .ecommerceorder import ECommerceOrder
        from .ecommerceproduct import ECommerceProduct
        from .ecommercepurchase import ECommercePurchase

        bill = None
        order = None
        purchase = None
        product = None
        is_order = False
        is_purchase = False
        is_product = False

        if isinstance(target, Bill):
            bill = target
            item = bill.item
        else:
            item = target

        if isinstance(item, ECommerceProduct):
            is_product = True
        elif isinstance(item, ECommerceOrder):
            is_order = True
        elif isinstance(item, ECommercePurchase):
            is_purchase = True
        else:
            raise ValueError(
                "ECommerceBillingConcept.applies_to() expected "
                "an instance of Bill, ECommerceProduct or ECommerceOrder, "
                "got %r instead"
                % target
            )

        if not self.enabled:
            return False

        if not self.is_current():
            return False

        if is_product:

            if self.eligible_products and item not in self.eligible_products:
                return False

            product = item

        elif self.scope == "order":

            if not is_order:
                return False

            if self.eligible_products and not any(
                purchase.product in self.eligible_products
                for purchase in item.purchases
            ):
                return False

            order = item

        elif self.scope == "purchase":

            if not is_purchase:
                return False

            if self.eligible_products \
            and item.product not in self.eligible_products:
                return False

            order = item.order
            purchase = item
            product = item.product

        if self.eligible_countries and (
            order is None
            or order.country is None
            or not any(
                order.country.descends_from(region)
                for region in self.eligible_countries
            )
        ):
            return False

        # Eligible roles
        if self.eligible_roles and (
            order is None
            or order.customer is None
            or not any(
                role in self.eligible_roles
                for role in order.customer.iter_roles()
            )
        ):
            return False

        # Custom condition
        if self.condition:
            context = {
                "self": self,
                "order": order,
                "purchase": purchase,
                "product": product,
                "bill": bill,
                "applies": True
            }
            exec self.condition in context
            if not context["applies"]:
                return False

        return True

    def apply(self, bill_node):

        item = bill_node.bill.item
        method, value = self.parse_implementation()
        bill_node._concept_method = method
        bill_node._concept_value = value

        if method == "override":
            bill_node._delete_preceding(
                lambda prev: prev.concept_method in ("add", "override")
            )
            bill_node._cost = value

        elif method == "add":
            bill_node._cost += value

        elif method == "override_percentage":
            bill_node._delete_preceding(
                lambda prev: prev.concept_method in (
                    "add_percentage",
                    "override_percentage"
                )
            )
            base_cost = bill_node.bill.pricing.base.cost
            bill_node._cost = base_cost + base_cost * value / 100

        elif method == "add_percentage":
            bill_node._cost += bill_node.bill.pricing.cost * value / 100

        elif method == "free_units":
            delivered, paid = value
            q, r = divmod(item.quantity, delivered)
            bill_node._paid_units = q * paid + r

        elif method == "custom":
            context = {
                "self": self,
                "item": item,
                "bill": bill_node.bill,
                "bill_node": bill_node,
                "Decimal": Decimal
            }
            exec value in context

    def parse_implementation(self):

        value = self.implementation

        # Cost override
        match = override_regexp.match(value)
        if match:
            return ("override", Decimal(match.group(1)))

        # Additive cost
        match = add_regexp.match(value)
        if match:
            return ("add", Decimal(match.group(1)))

        # Override percentage
        match = override_percentage_regexp.match(value)
        if match:
            return ("override_percentage", Decimal(match.group(1)))

        # Override percentage
        match = add_percentage_regexp.match(value)
        if match:
            return ("add_percentage", Decimal(match.group(1)))

        # Free units discount ("3x2", "2x1", etc)
        match = free_units_regexp.match(value)
        if match:
            return ("free_units", (int(match.group(1)), int(match.group(2))))

        return ("custom", value)

