#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Extension, Controller, Configuration
from woost.models.rendering import ChainRenderer


translations.define("IssuuExtension",
    ca = u"Documents Issuu",
    es = u"Documentos Issuu",
    en = u"Issuu documents"
)

translations.define("FacebookPublicationExtension-plural",
    ca = u"Documents Issuu",
    es = u"Documentos Issuu",
    en = u"Issuu documents"
)


class IssuuExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afegeix suport per documents Issuu""",
            "ca"
        )   
        self.set("description",                
            u"""Añade soporte para documentos Issuu""",
            "es"
        )   
        self.set("description",
            u"""Adds support for Issuu documents""",
            "en"
        )

    def _load(self):
     
        from woost.extensions.issuu import (
            strings,
            issuudocument,
            issuublock
        )   
     
    def _install(self):

        # Create the product controller
        controller = Controller()
        controller.qname = "woost.issuu_document_controller"
        for language in Configuration.instance.languages:
            value = translations(
                "woost.extensions.issuu.issuu_document_controller.title",
                language
            )   
            if value:
                controller.set("title", value, language)
        controller.python_name = \
            "woost.extensions.issuu.issuudocumentcontroller.IssuuDocumentController"
        controller.insert()

        self._create_renderers()

    def _create_renderers(self):

        from woost.extensions.issuu.issuudocumentrenderer \
            import IssuuDocumentRenderer                                                                                                     

        # Look for the first chain renderer
        for renderer in Configuration.instance.renderers:
            if isinstance(renderer, ChainRenderer):

                # Add the renderer for Issuu documents
                issuu_renderer = IssuuDocumentRenderer()
                issuu_renderer.insert()
                renderer.renderers.append(issuu_renderer)

                break

