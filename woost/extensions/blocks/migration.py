#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import MigrationStep

step = MigrationStep("woost.extensions.blocks Add video renderers")

@when(step.executing)
def add_video_renderers(e):

    from woost.models import Configuration
    from woost.models.rendering import ChainRenderer
    from woost.extensions.blocks.youtubeblockrenderer import YouTubeBlockRenderer
    from woost.extensions.blocks.vimeoblockrenderer import VimeoBlockRenderer

    # Look for the first chain renderer
    for renderer in Configuration.instance.renderers:
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

    from woost.models import Configuration, Style
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
                    for language in Configuration.instance.languages:
                        style.set("title", css_class, language)
                    style.insert()

                style.applicable_to_blocks = True
                block.styles.append(style)

            del block._css_class

#------------------------------------------------------------------------------
step = MigrationStep("woost.extensions.blocks Convert video blocks")

@when(step.executing)
def convert_video_blocks(e):
    from woost.extensions.youtube.youtubevideo import YouTubeVideo
    from woost.extensions.vimeo.vimeovideo import VimeoVideo
    from woost.extensions.blocks.youtubeblock import YouTubeBlock
    from woost.extensions.blocks.youtubeblockrenderer import YouTubeBlockRenderer
    from woost.extensions.blocks.vimeoblock import VimeoBlock
    from woost.extensions.blocks.vimeoblockrenderer import VimeoBlockRenderer
    from woost.extensions.blocks.videoblock import VideoBlock

    YouTubeBlockRenderer.select().delete_items()
    VimeoBlockRenderer.select().delete_items()

    for old_block_model, video_model in (
        (YouTubeBlock, YouTubeVideo),
        (VimeoBlock, VimeoVideo)
    ):
        for old_block in old_block_model.select():
            block = VideoBlock()
            block.video = video_model(video_id = old_block.video_id)

            for lang in old_block.translations:
                title = old_block.get("heading", lang)
                block.video.set("title", title, lang)
                block.set("heading", title, lang)

            block.insert()
            old_block.replace_with(block)
            old_block.delete()

#------------------------------------------------------------------------------
step = MigrationStep("woost.extensions.blocks Convert file listing blocks")

@when(step.executing)
def convert_file_listing_blocks(e):
    from woost.extensions.blocks.filelisting import FileListing
    from woost.extensions.blocks.publishablelisting import PublishableListing

    for old_block in FileListing.select():
        block = PublishableListing()
        block.element_type = old_block.element_type
        block.publishables = old_block.files
        block.links_open_in_new_window = old_block.links_open_in_new_window

        if old_block.listing_order in \
            PublishableListing.listing_order.enumeration:
            block.listing_order = old_block.listing_order

        for lang in old_block.translations:
            title = old_block.get("heading", lang)
            block.set("heading", title, lang)

        block.insert()
        old_block.replace_with(block)
        old_block.delete()
