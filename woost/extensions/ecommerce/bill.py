#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from abc import ABCMeta, abstractproperty
from decimal import Decimal
from collections import OrderedDict
from woost import app


class BillNode(object):

    __metaclass__ = ABCMeta

    _bill = None
    _section = None
    _prev = None
    _next = None

    _concept = None
    _concept_method = None
    _concept_value = None

    _cost = Decimal("0.00")
    _total = Decimal("0.00")

    @property
    def bill(self):
        return self._bill

    @property
    def section(self):
        return self._section

    @property
    def base(self):
        node = self
        while node._prev:
            node = node._prev
        return node

    @property
    def previous(self):
        return self._prev

    @property
    def next(self):
        return self._next

    @property
    def concept(self):
        return self._concept

    @property
    def concept_method(self):
        return self._concept_method

    @property
    def concept_value(self):
        return self._concept_value

    @property
    def cost(self):
        return self._cost

    @property
    def base_cost(self):
        return self._prev._cost if self._prev else Decimal("0.00")

    @property
    def cost_differential(self):
        return self._cost - self.base_cost

    @property
    def total(self):
        return self._total

    @property
    def base_total(self):
        return self._prev._total if self._prev else Decimal("0.00")

    @property
    def total_differential(self):
        return self._total - self.base_total

    def _copy_node(self, node):
        self._cost = node._cost
        self._total = node._total

    def _delete(self):

        bill = self._bill

        if bill is None:
            raise ValueError(
                "Can't delete a node that's not attached to a bill"
            )

        prev = self._prev

        if prev is None:
            raise ValueError("Can't remove the root node from a bill")

        next = self._next

        self._bill = None
        self._prev = None
        self._next = None

        prev._next = next

        if next:
            next._prev = prev
        else:
            setattr(bill, "_" + self._type, prev)

    def _delete_nodes(self, filter):
        node = self
        while node and node._prev:
            previous = node._prev
            if filter(node):
                node._delete()
            node = previous

    def _delete_preceding(self, filter):
        if self._prev:
            self._prev._delete_nodes(filter)

    def ascend(self):
        node = self
        while node:
            yield node
            node = node._prev

    def list_concept_nodes(self):
        nodes = list(node for node in self.ascend() if node._concept)
        nodes.reverse()
        return nodes

    def list_concepts(self):
        concepts = list(
            node._concept
            for node in self.ascend()
            if node._concept
        )
        concepts.reverse()
        return concepts

    def find_concept(self, concept):

        for node in self.ascend():
            if node._concept is concept:
                return node

        return None


class OrderNode(BillNode):
    pass


class PurchaseNode(BillNode):

    _quantity = None
    _paid_units = None

    @property
    def quantity(self):
        return self._quantity

    @property
    def paid_units(self):
        return self._paid_units

    def _copy_node(self, node):
        BillNode._copy_node(self, node)
        self._paid_units = node._paid_units


class Bill(object):

    __metaclass__ = ABCMeta

    _node_class = abstractproperty()

    _item = None
    _pricing = None
    _shipping = None
    _taxes = None

    _cost = Decimal("0.00")
    _total = Decimal("0.00")

    def __init__(self, item):

        self._item = item

        self._pricing = self._node_class()
        self._pricing._bill = self
        self._pricing._section = "pricing"

        self._shipping = self._node_class()
        self._shipping._bill = self
        self._shipping._section = "shipping"

        self._taxes = self._node_class()
        self._taxes._bill = self
        self._taxes._section = "taxes"

    @property
    def item(self):
        return self._item

    @property
    def pricing(self):
        return self._pricing

    @property
    def shipping(self):
        return self._shipping

    @property
    def taxes(self):
        return self._taxes

    @property
    def cost(self):
        return self._cost

    @property
    def total(self):
        return self._total

    def _add_concept(self, section, concept):

        node = self._node_class()
        node._concept = concept
        key = "_" + section
        current = getattr(self, key)
        setattr(self, key, node)
        node._bill = self
        node._section = section

        node._prev = current
        if current:
            current._next = node
            node._copy_node(current)

        concept.apply(node)
        return node

    def _update_total(self):
        self._total = (
            self.pricing.total
            + self.shipping.total
            + self.taxes.total
        )

class OrderBill(Bill):

    _node_class = OrderNode

    def __init__(self,
        order,
        pricing = None,
        shipping = None,
        taxes = None
    ):
        Bill.__init__(self, order)
        self._purchases = OrderedDict()

        # Default policies
        if pricing is None:
            pricing = app.website.ecommerce_pricing

        if shipping is None:
            shipping = app.website.ecommerce_shipping_costs

        if taxes is None:
            taxes = app.website.ecommerce_taxes

        # Per purchase costs:
        for purchase in order.purchases:
            PurchaseBill(
                self,
                purchase,
                pricing = pricing,
                shipping = shipping,
                taxes = taxes
            )

        # Pricing
        self.pricing._total = self.pricing.cost

        for concept in pricing:
            if concept.applies_to(self):
                self._add_concept("pricing", concept)
                self.pricing._total = self.pricing.cost

        # Order shipping costs
        self.shipping._total = self.shipping.cost

        for concept in shipping:
            if concept.applies_to(self):
                self._add_concept("shipping", concept)
                self.shipping._total = self.shipping.cost

        # Order taxes
        self.taxes._total = self.taxes.cost

        for concept in taxes:
            if concept.applies_to(self):
                self._add_concept("taxes", concept)
                self.taxes._total = self.taxes.cost

        self._update_total()

    @property
    def purchases(self):
        return self._purchases


class PurchaseBill(Bill):

    _node_class = PurchaseNode
    _bill = None

    def __init__(
        self,
        bill,
        purchase,
        pricing = None,
        shipping = None,
        taxes = None
    ):
        Bill.__init__(self, purchase)

        # Attach the purchase bill to the order bill
        self._bill = bill
        bill._purchases[purchase] = self

        # Set initial quantities
        for node in self._pricing, self._shipping, self._taxes:
            node._quantity = node._paid_units = purchase.quantity

        # Default policies
        website = app.website

        if pricing is None:
            pricing = app.website.ecommerce_pricing

        if shipping is None:
            shipping = app.website.ecommerce_shipping_costs

        if taxes is None:
            taxes = app.website.ecommerce.taxes

        # Calculate the base per unit cost
        self.pricing._cost = purchase.get_unit_price()

        # Pricing
        self.pricing._total = self.pricing.cost * self.pricing.paid_units

        for concept in pricing:
            if concept.applies_to(self):
                self._add_concept("pricing", concept)
                self.pricing._total = \
                    self.pricing.cost * self.pricing.paid_units

        # Shipping
        self.shipping._total = self.shipping.cost * self.shipping.paid_units

        for concept in shipping:
            if concept.applies_to(self):
                self._add_concept("shipping", concept)
                self.shipping._total = \
                    self.shipping.cost * self.shipping.paid_units

        # Taxes
        self.taxes._total = self.taxes.cost * self.taxes.paid_units

        for concept in taxes:
            if concept.applies_to(self):
                self._add_concept("taxes", concept)
                self.taxes._total = self.taxes.cost * self.taxes.paid_units

        # Total
        self._update_total()

        # Update the order bill costs
        bill.pricing._cost += self.pricing.total
        bill.shipping._cost += self.shipping.total
        bill.taxes._cost += self.taxes.total

