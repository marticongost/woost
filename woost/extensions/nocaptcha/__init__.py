#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Víctor Manuel Agüero Requena <victor.aguero@whads.com>
"""
from cocktail.translations import translations
from woost.models import Extension

translations.load_bundle("woost.extensions.nocaptcha.package")

class NoCaptchaExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afegeix suport pel servei anti-bots noCAPTCHA.""",
            "ca"
        )
        self.set("description",
            u"""Añade soporte para el servicio anti-bots noCAPTCHA.""",
            "es"
        )
        self.set("description",
            u"""Adds suport for anti-bots noCAPTCHA service.""",
            "en"
        )

    def _load(self):
        from woost.extensions.nocaptcha import configuration, website

