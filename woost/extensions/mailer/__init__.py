#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from cocktail.events import event_handler, when
from cocktail import schema
from cocktail.translations import translations
from cocktail.controllers import context
from woost.models import Extension, Document, Template


translations.define("MailerExtension",
    ca = u"Enviament de documents per correu electrònic",
    es = u"Envio de documentos por correo electrónico",
    en = u"Sending documents by email"
)

translations.define("MailerExtension-plural",
    ca = u"Enviament de documents per correu electrònic",
    es = u"Envio de documentos por correo electrónico",
    en = u"Sending documents by email"
)


class MailerExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet enviar documents per correu electrònic.""",
            "ca"
        )
        self.set("description",            
            u"""Permite enviar documents por correo electrónico.""",
            "es"
        )
        self.set("description",
            u"""Allows send documents by email.""",
            "en"
        )


    @event_handler
    def handle_loading(cls, event):
 
        extension = event.source

        from woost.controllers.backoffice.itemcontroller import \
            ItemController

        from woost.extensions.mailer import (
            useraction,
            strings
        )

        from woost.extensions.mailer.sendemailcontroller import \
            SendEmailController

        ItemController.send_email = SendEmailController

        Document.send_email_view = "woost.extensions.mailer.SendEmailView"
        Template.add_member(
            schema.Boolean(
                "per_user_customizable",
                default = False,
                listed_by_default = False
            )
        )
        Template.members_order.append("per_user_customizable")
    
        # Disable interactive features from rendered pages when rendering
        # static content
        from woost.controllers.application import CMS
    
        @when(CMS.producing_output)
        def disable_user_controls(event):
            if context.get("sending_email", False):
                event.output["show_user_controls"] = False

