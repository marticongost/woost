#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.translations import translations
from cocktail import schema
from tpv.sis import SISPaymentGateway as Implementation
from woost.models import Document
from woost.extensions.payments.paymentgateway import PaymentGateway


class SISPaymentGateway(PaymentGateway, Implementation):

    instantiable = True

    default_label = schema.DynamicDefault(
        lambda: translations("SISPaymentGateway.label default")
    )

    members_order = [
        "merchant_name",
        "merchant_code",
        "merchant_terminal",
        "merchant_secret_key",
        "pay_methods",
        "payment_successful_page",
        "payment_failed_page"
    ]

    merchant_code = schema.String(
        required = True,
        shadows_attribute = True,
        text_search = False
    )

    merchant_name = schema.String(
        shadows_attribute = True,
        text_search = False
    )

    merchant_terminal = schema.String(
        required = True,
        shadows_attribute = True,
        text_search = False
    )

    merchant_secret_key = schema.String(
        required = True,
        shadows_attribute = True,
        text_search = False
    )

    pay_methods = schema.Collection(
        shadows_attribute = True,
        items = schema.String(
            enumeration = ["T", "D", "R"],
            translate_value = (
                lambda value, language = None, **kwargs:
                    "" if not value
                    else translations(
                        "woost.extensions.payments.sis.SISPaymentGateway."
                        "members.pay_methods.items.values.%s"
                        % value,
                        language
                    )
            )
        ),
        edit_control = "cocktail.html.CheckList"
    )

    payment_successful_page = schema.Reference(
        type = Document,
        related_end = schema.Reference()
    )

    payment_failed_page = schema.Reference(
        type = Document,
        related_end = schema.Reference()
    )

