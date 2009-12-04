#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández Camps
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from cocktail.modeling import OrderedDict
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.language import get_content_language
from cocktail import schema
from cocktail.controllers.location import Location
from sitebasis.models import Extension

translations.define("ReCaptchaExtension",
    ca = u"ReCaptcha",
    es = u"ReCaptcha",
    en = u"ReCaptcha"
)

translations.define("ReCaptchaExtension-plural",
    ca = u"ReCaptcha",
    es = u"ReCaptcha",
    en = u"ReCaptcha"
)

translations.define("ReCaptchaExtension.public_key",
    ca = u"Clau pública",
    es = u"Clave pública",
    en = u"Public key"
)

translations.define("ReCaptchaExtension.private_key",
    ca = u"Clau privada",
    es = u"Clave privada",
    en = u"Private key"
)

translations.define("ReCaptchaExtension.theme",
    ca = u"Tema",
    es = u"Tema",
    en = u"Theme"
)

translations.define("ReCaptchaExtension.ssl",
    ca = u"SSL",
    es = u"SSL",
    en = u"SSL"
)


class ReCaptchaExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afageix suport pel servei anti-bots reCAPTCHA.""",
            "ca"
        )
        self.set("description",            
            u"""Añade soporte para el servicio anti-bots reCAPTCA.""",
            "es"
        )
        self.set("description",
            u"""Adds support for anti-bot reCAPTCHA service.""",
            "en"
        )

    @event_handler
    def handle_loading(cls, event):

        # Import the extension's models
        from sitebasis.extensions.recaptcha.schemarecaptchas import ReCaptcha
        from sitebasis.extensions.recaptcha import (
            strings
        )

        # Append additional members to the extension                            
        ReCaptchaExtension.members_order = [
            "public_key", "private_key", "theme", "ssl"
        ]

        ReCaptchaExtension.add_member(
            schema.String(
                "public_key",
                required = True
            )   
        )

        ReCaptchaExtension.add_member(
            schema.String(
                "private_key",
                required = True
            )   
        )

        ReCaptchaExtension.add_member(
            schema.String(
                "theme",
                required = True,
                enumeration = (
                    "red", "white", "blackglass", "clean", "custom"
                ),
                default = "red"
            )   
        )

        ReCaptchaExtension.add_member(
            schema.Boolean(
                "ssl",
                default = False
            )   
        )

