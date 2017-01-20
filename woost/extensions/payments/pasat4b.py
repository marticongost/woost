#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail import schema
from cocktail.translations import translations
from tpv.pasat4b import Pasat4bPaymentGateway as Implementation
from woost.extensions.payments.paymentgateway import PaymentGateway


class Pasat4bPaymentGateway(PaymentGateway, Implementation):

    instantiable = True

    default_label = schema.DynamicDefault(
        lambda: translations(
            "woost.extensions.payments.pasat4b.Pasat4bPaymentGateway."
            "default_label"
        )
    )

    merchant_code = schema.String(
        required = True,
        shadows_attribute = True,
        text_search = False
    )

