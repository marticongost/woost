#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from sitebasis.models import Extension, Document

translations.define("PaymentsExtension",
    ca = u"Pagaments",
    es = u"Pagos",
    en = u"Payments"
)

translations.define("PaymentsExtension-plural",
    ca = u"Pagaments",
    es = u"Pagos",
    en = u"Payments"
)


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

    @event_handler
    def handle_loading(cls, event):

        # Import the extension's models
        from sitebasis.extensions.payments.paymentgateway import PaymentGateway
        from sitebasis.extensions.payments import (
            strings,
            pasat4b
        )

        # Setup payment controllers
        from sitebasis.controllers.application import CMS        
        from sitebasis.extensions.payments.paymenthandshakecontroller \
            import PaymentHandshakeController
        from sitebasis.extensions.payments.paymentnotificationcontroller \
            import PaymentNotificationController
        
        CMS.payment_handshake = PaymentHandshakeController
        CMS.payment_notification = PaymentNotificationController
        
        # Append additional members to the extension
        PaymentsExtension.members_order = [
            "payment_gateway",
            "payment_successful_page",
            "payment_failed_page"
        ]

        PaymentsExtension.add_member(
            schema.Reference("payment_gateway",
                type = PaymentGateway,
                related_end = schema.Reference()
            )
        )

        PaymentsExtension.add_member(
            schema.Reference("payment_successful_page",
                type = Document,
                related_end = schema.Reference()
            )
        )

        PaymentsExtension.add_member(
            schema.Reference("payment_failed_page",
                type = Document,
                related_end = schema.Reference()
            )
        )

