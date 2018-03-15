#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from woost.models import Extension, Configuration, VideoPlayerSettings
from woost.models.rendering import ChainRenderer

translations.load_bundle("woost.extensions.vimeo.package")


class VimeoExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afegeix suport per vídeos de Vimeo""",
            "ca"
        )
        self.set("description",
            u"""Añade soporte para videos de Vimeo""",
            "es"
        )
        self.set("description",
            u"""Adds support for Vimeo videos""",
            "en"
        )

    def _load(self):
        from woost.extensions.vimeo import (
            vimeovideo,
            videoplayersettings
        )

        self.install()

    def _install(self):
        self._create_renderers()

    def _create_renderers(self):

        from woost.extensions.vimeo.vimeovideorenderer \
            import VimeoVideoRenderer

        # Add the renderer for Vimeo videos
        content_renderer = ChainRenderer.get_instance(
            qname = "woost.content_renderer"
        )
        if content_renderer:
            content_renderer.renderers.append(VimeoVideoRenderer.new())

