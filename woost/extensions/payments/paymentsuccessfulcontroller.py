#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
from cocktail import schema
from cocktail.controllers import request_property, get_parameter
from woost.controllers.publishablecontroller import PublishableController
from woost.extensions.payments.paymentgateway import PaymentGateway


class PaymentSuccessfulController(PublishableController):

    @request_property
    def output(self):
        output = PublishableController.output(self)

        payment_gateway = get_parameter(
            schema.Reference(
                "payment_gateway",
                type = PaymentGateway,
                required = True
            )
        )

        if payment_gateway:
            payment = payment_gateway.get_request_payment()
            if payment:
                html = output.get("body_beginning_html") or ""
                html += u"""
                <script type="text/javascript">
                    if (typeof(ga) != undefined) {
                        ga("require", "ecommerce");
                        ga("ecommerce:addTransaction", %s); %s
                        ga("ecommerce:send");
                    }
                </script>
                """ % (
                    json.dumps(self.get_ga_transaction_for_payment(payment)),
                    u"".join(
                        u"""ga("ecommerce:addItem", %s);""" % json.dumps(item)
                        for item in self.iter_ga_items_for_payment(payment)
                    )
                )
                output["body_beginning_html"] = html

        return output

    def get_ga_transaction_for_payment(self, payment):
        return {
            "id": str(payment.id),
            "revenue": str(payment.amount),
            "currency": payment.currency.alpha
        }

    def iter_ga_items_for_payment(self, payment):
        return []

