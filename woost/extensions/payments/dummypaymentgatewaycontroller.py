#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from urllib import urlopen
import cherrypy
from woost.models import get_current_website
from woost.extensions.payments.paymentgatewaycontroller \
    import PaymentGatewayController


class DummyPaymentGatewayController(PaymentGatewayController):
    """A controller used by L{DummyPaymentGateway
    <woost.extensions.payments.dummypaymentgateway.DummyPaymentGateway>}
    instances to simulate transaction payments.
    """
    
    @cherrypy.expose
    def simulate_transaction(self, **parameters):

        payment_id = parameters.get("payment_id")
        payment = payment_id and self.payment_gateway.get_payment(payment_id)

        if not payment:
            raise cherrypy.NotFound()

        # Notify the payment to the application
        notification_url = payment.get_payment_url(
            "notification",
            payment_id = str(payment.id)
        )
        urlopen(str(notification_uri))

        # Redirect the user after the transaction's over
        redirection = None

        if gateway.payment_status == "accepted":
            redirection = gateway.payment_successful_page
        elif gateway.payment_status == "failed":
            redirection = gateway.payment_failed_page
            
        if redirection is None:
            redirection = get_current_website().home
        
        raise cherrypy.HTTPRedirect(redirection.get_uri(host = "!"))

