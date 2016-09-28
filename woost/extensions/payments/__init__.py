#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Extension

translations.load_bundle("woost.extensions.payments.package")


class PaymentsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afageix suport per pagaments en línia.""",
            "ca"
        )
        self.set("description",
            u"""Añade soporte para pagos en linea.""",
            "es"
        )
        self.set("description",
            u"""Adds support for online payments.""",
            "en"
        )

    def _load(self):

        # Import the extension's models
        from woost.extensions.payments.paymentgateway import PaymentGateway
        from woost.extensions.payments import (
            dummypaymentgateway,
            pasat4b,
            sis,
            paypal,
            transactionnotifiedtrigger
        )

        # Setup payment controllers
        from woost.controllers.cmscontroller import CMSController
        from woost.extensions.payments.paymentrootcontroller \
            import PaymentRootController

        CMSController.payments = PaymentRootController

