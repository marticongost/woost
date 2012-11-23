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

step = MigrationStep("woost.extensions.blocks Model block styles")

@when(step.executing)
def model_block_styles(e):

    from woost.models import Style, Language
    from woost.extensions.blocks.block import Block

    for style in Style.select():
        style.applicable_to_blocks = False

    for block in Block.select():
        
        value = getattr(block, "_css_class", None)

        if value is not None:
            for css_class in value.split():
                style = Style.get_instance(custom_class_name = css_class)

                if style is None:
                    style = Style()
                    style.custom_class_name = css_class
                    for language in Language.codes:
                        style.set("title", css_class, language)
                    style.insert()

                style.applicable_to_blocks = True
                block.styles.append(style)

            del block._css_class

