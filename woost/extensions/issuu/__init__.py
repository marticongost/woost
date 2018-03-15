#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Extension, Controller, Configuration
from woost.models.rendering import ChainRenderer

translations.load_bundle("woost.extensions.issuu.package")


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
            issuudocument,
            issuublock,
        )
        self.install()
        self.register_view_factory()

    def _install(self):

        translations.load_bundle("woost.extensions.issuu.installation")

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

        content_renderer = ChainRenderer.get_instance(
            qname = "woost.content_renderer"
        )
        if content_renderer:
            content_renderer.renderers.append(IssuuDocumentRenderer.new())

    def register_view_factory(self):

        from cocktail.html import templates
        from woost.extensions.issuu.issuudocument import IssuuDocument
        from woost.views.viewfactory import (
            publishable_view_factory,
            publishable_grid_view_factory
        )

        def issuu_viewer(item, parameters):
            viewer = templates.new("cocktail.html.IssuuViewer")
            viewer.config_id = item.issuu_config_id
            viewer.page_number = item.thumbnail_page
            return viewer

        publishable_view_factory.register_first(
            IssuuDocument,
            "issuu_viewer",
            issuu_viewer
        )

        publishable_grid_view_factory.register_first(
            IssuuDocument,
            "issuu_viewer",
            issuu_viewer
        )

