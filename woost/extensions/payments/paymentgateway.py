"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from tpv.currencies import currency_alpha
from cocktail.modeling import OrderedDict
from cocktail.events import Event
from cocktail.translations import translations, get_language
from cocktail import schema
from cocktail.controllers import post_redirection
from woost import app
from woost.models import Item


class PaymentGateway(Item):

    instantiable = False
    visible_from_root = False
    payment_gateway_controller_class = \
        "woost.extensions.payments.paymentgatewaycontroller.PaymentGatewayController"

    transaction_notified = Event(
        """An event triggered when the payment gateway notifies the application
        of the outcome of a payment transaction.

        @param payment: The payment that the notification is sent for.
        @type payment: L{Payment<tpv.payment.Payment>}
        """
    )

    members_order = [
        "label",
        "test_mode",
        "currency"
    ]

    label = schema.String(
        required = True,
        translated = True
    )

    test_mode = schema.Boolean(
        required = True,
        default = True
    )

    currency = schema.String(
        required = True,
        enumeration = currency_alpha,
        translatable_enumeration = False,
        text_search = False
    )

    def __translate__(self, language, **kwargs):
        return translations(self.__class__.name, language)

    def initiate_payment(self, payment_id):
        """Begin a payment transaction, redirecting the user to the payment
        gateway.

        @param payment_id: The identifier of the payment to execute.
        """
        url, params = self.get_payment_form_data(payment_id, get_language())
        post_redirection(url, OrderedDict(params))

    def get_payment_url(self, *args, **kwargs):
        return app.url_mapping.get_url(
            path = ["payments", str(self.id)] + list(args),
            parameters = kwargs
        )

    @property
    def handshake_url(self):
        return self.get_payment_url("handshake")

    @property
    def notification_url(self):
        return self.get_payment_url("notification")

