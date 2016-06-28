#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from woost.models import Extension, Configuration
from woost.models.rendering import ChainRenderer

translations.load_bundle("woost.extensions.tv3alacarta.package")


class TV3ALaCartaExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afegeix suport per vídeos del 'TV3 a la carta'""",
            "ca"
        )
        self.set("description",
            u"""Añade soporte para videos del servicio 'TV3 a la carta'""",
            "es"
        )
        self.set("description",
            u"""Adds support for videos from the 'TV3 a la carta' service""",
            "en"
        )

    def _load(self):
        from woost.extensions.tv3alacarta import (
            tv3alacartavideo,
            videoplayersettings
        )

