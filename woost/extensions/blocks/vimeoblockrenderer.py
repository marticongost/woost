#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from simplejson import loads
from urllib2 import urlopen
from woost.models.rendering import ImageURIRenderer
from woost.extensions.blocks.vimeoblock import VimeoBlock

METADATA_URL_PATTERN = "http://vimeo.com/api/v2/video/%s.json"

def get_video_metadata(video_id, timeout = 15):
    url = METADATA_URL_PATTERN % video_id
    json = urlopen(url, timeout = timeout).read()
    return loads(json)[0]


class VimeoBlockRenderer(ImageURIRenderer):

    def can_render(self, item, **parameters):
        return isinstance(item, VimeoBlock) and item.video_id

    def get_item_uri(self, item):
        return get_video_metadata(item.video_id)["thumbnail_large"]

