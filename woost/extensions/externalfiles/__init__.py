#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from woost.models import Extension, Configuration, Website

translations.load_bundle("woost.extensions.externalfiles.package")


class ExternalFilesExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afegeix suport per fitxers externs""",
            "ca"
        )
        self.set("description",
            u"""Añade soporte para ficheros externos""",
            "es"
        )
        self.set("description",
            u"""Adds support for external files""",
            "en"
        )

    def _load(self):
        from woost.extensions.externalfiles import (
            configuration,
            website,
            item,
            publishable
        )

        self.install()

