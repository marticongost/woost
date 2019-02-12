#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from woost.extensions.payments.paymentsuccessfulcontroller import \
    PaymentSuccessfulController


class OrderSuccessfulController(PaymentSuccessfulController):

    def get_ga_transaction_for_payment(self, payment):

        transaction = (
            PaymentSuccessfulController
            .get_ga_transaction_for_payment(self, payment)
        )

        order = payment.order
        transaction["shipping"] = str(order.total_shipping_costs)
        transaction["tax"] = str(order.total_taxes)
        return transaction

    def iter_ga_items_for_payment(self, payment):
        for purchase, bill in payment.order.bill.purchases.iteritems():
            yield {
                "id": purchase.product.id,
                "name": translations(purchase.product),
                "price": str(bill.pricing.cost),
                "quantity": purchase.quantity
            }

