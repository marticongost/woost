#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models.rendering import ImageURIRenderer
from woost.extensions.blocks.youtubeblock import YouTubeBlock

THUMBNAIL_URL_PATTERN = "http://img.youtube.com/vi/%s/0.jpg"


class YouTubeBlockRenderer(ImageURIRenderer):

    def can_render(self, item, **parameters):
        return isinstance(item, YouTubeBlock) and item.video_id

    def get_item_uri(self, item):
        return THUMBNAIL_URL_PATTERN % item.video_id

