#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail import schema
from cocktail.controllers import get_parameter, redirect
from woost import app
from woost.controllers.basecmscontroller import BaseCMSController
from woost.extensions.payments.dummypaymentgateway \
    import DummyPaymentGateway
from urllib import urlopen


class DummyPaymentGatewayController(BaseCMSController):
    """A controller used by L{DummyPaymentGateway
    <woost.extensions.payments.dummypaymentgateway.DummyPaymentGateway>}
    instances to simulate transaction payments.
    """

    def __call__(self, **parameters):

        # Get references to the gateway and payment
        gateway = get_parameter(
            schema.Reference("gateway_id", type = DummyPaymentGateway)
        )

        if gateway is None:
            raise ValueError("Wrong payment gateway")

        payment_id = get_parameter(schema.String("payment_id"))
        payment = payment_id and gateway.get_payment(payment_id) or None

        if payment is None:
            raise ValueError("Wrong payment id (%s)" % payment_id)

        # Notify the payment to the application
        cms = self.context["cms"]
        notification_uri = app.url_mapping.get_url(
            path = ["payment_notification"],
            parameters = {"payment_id": payment_id}
        )
        urlopen(notification_uri)

        # Redirect the user after the transaction's over
        destination = None

        if gateway.payment_status == "accepted":
            destination = gateway.payment_successful_page
        elif gateway.payment_status == "failed":
            destination = gateway.payment_failed_page

        redirect((destination or app.website.home).get_uri())

