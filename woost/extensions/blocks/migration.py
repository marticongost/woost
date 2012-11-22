#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import MigrationStep

step = MigrationStep("woost.extensions.blocks Add video renderers")

@when(step.executing)
def add_video_renderers(e):

    from woost.models import Site
    from woost.models.rendering import ChainRenderer
    from woost.extensions.blocks.youtubeblockrenderer import YouTubeBlockRenderer
    from woost.extensions.blocks.vimeoblockrenderer import VimeoBlockRenderer

    # Look for the first chain renderer
    for renderer in Site.main.renderers:
        if isinstance(renderer, ChainRenderer):

            # Add the renderer for YouTube blocks
            youtube_renderer = YouTubeBlockRenderer()
            youtube_renderer.insert()
            renderer.renderers.append(youtube_renderer)

            # Add the renderer for Vimeo blocks
            vimeo_renderer = VimeoBlockRenderer()
            vimeo_renderer.insert()
            renderer.renderers.append(vimeo_renderer)

            break

