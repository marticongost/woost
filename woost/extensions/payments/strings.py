#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.translations import translations

# TransactionNotifiedTrigger
#------------------------------------------------------------------------------
translations.define("TransactionNotifiedTrigger",
    ca = u"Disparador de notificació de pagament",
    es = u"Disparador de notificación de pago",
    en = u"Payment notification trigger"
)

translations.define("TransactionNotifiedTrigger-plural",
    ca = u"Disparadors de notificació de pagament",
    es = u"Disparadores de notificación de pago",
    en = u"Payment notification triggers"
)

# DummyPaymentGateway
#------------------------------------------------------------------------------
translations.define("DummyPaymentGateway",
    ca = u"Passarel·la de pagaments simulada",
    es = u"Pasarela de pagos simulada",
    en = u"Dummy payment gateway"
)

translations.define("DummyPaymentGateway-plural",
    ca = u"Passarel·les de pagaments simulades",
    es = u"Pasarelas de pagos simuladas",
    en = u"Dummy payment gateways"
)

translations.define("DummyPaymentGateway.payment_status",
    ca = u"Resultat dels pagaments",
    es = u"Resultado de los pagos",
    en = u"Payment outcome"
)

translations.define("DummyPaymentGateway.payment_successful_page",
    ca = u"Pàgina de confirmació de pagament",
    es = u"Página de confirmación de pago",
    en = u"Payment successful page"
)

translations.define("DummyPaymentGateway.payment_failed_page",
    ca = u"Pàgina de pagament fallit",
    es = u"Página de pago fallido",
    en = u"Payment failed page"
)

translations.define(
    "woost.extensions.payments.DummyPaymentGateway.payment_status "
    "accepted",
    ca = u"Acceptat",
    es = u"Aceptado",
    en = u"Accepted"
)

translations.define(
    "woost.extensions.payments.DummyPaymentGateway.payment_status "
    "failed",
    ca = u"Cancel·lat",
    es = u"Cancelado",
    en = u"Canceled"
)

# PayPalPaymentGateway
#------------------------------------------------------------------------------
translations.define("PayPalPaymentGateway",
    ca = u"PayPal",
    es = u"PayPal",
    en = u"PayPal"
)

translations.define("PayPalPaymentGateway-plural",
    ca = u"PayPal",
    es = u"PayPal",
    en = u"PayPal"
)

translations.define("PayPalPaymentGateway.business",
    ca = u"Compte de PayPal",
    es = u"Cuenta de PayPal",
    en = u"PayPal account"
)

translations.define("PayPalPaymentGateway.payment_successful_page",
    ca = u"Pàgina de confirmació de pagament",
    es = u"Página de confirmación de pago",
    en = u"Payment successful page"
)

translations.define("PayPalPaymentGateway.payment_failed_page",
    ca = u"Pàgina de pagament fallit",
    es = u"Página de pago fallido",
    en = u"Payment failed page"
)

translations.define("PayPalPaymentGateway.label default",
    ca = u"Targeta de crèdit / PayPal",
    es = u"Tarjeta de crédito / PayPal",
    en = u"Credit card / PayPal"
)

