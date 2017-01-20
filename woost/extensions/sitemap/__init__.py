#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from cocktail.translations import translations
from woost.models import Extension

translations.load_bundle("woost.extensions.sitemap.package")


class SitemapExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Genera un mapa de documents per optimitzar l'indexat del lloc
            web, seguint l'estàndard sitemap.org.""",
            "ca"
        )
        self.set("description",
            u"""Genera un mapa de documentos para optimizar el indexado del
            sitio, siguiendo el estándard sitemap.org.""",
            "es"
        )
        self.set("description",
            u"""Generates a document map to optimize the indexing of the site
            by web crawlers, following the sitemap.org standard.""",
            "en"
        )

    def _load(self):
        from woost.extensions.sitemap import (
            migration,
            publishable,
            sitemap,
            robots
        )
        self.install()

    def _install(self):

        from woost.models import (
            Publishable,
            Document,
            Controller,
            extension_translations
        )

        translations.load_bundle("woost.extensions.sitemap.installation")

        # Sitemap controller
        sitemap_controller = self._create_asset(
            Controller,
            "sitemap_controller",
            title = extension_translations,
            python_name =
                "woost.extensions.sitemap.sitemapcontroller.SitemapController"
        )

