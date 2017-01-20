#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.events import when
from cocktail import schema
from cocktail.controllers import request_property
from woost.models import Publishable, VideoPlayerSettings
from .block import Block


class VideoBlock(Block):

    instantiable = True
    block_display = "woost.views.VideoBlockDisplay"
    views = [
        "woost.views.VideoBlockView",
        "woost.views.VideoPopUp"
    ]
    default_view_class = "woost.views.VideoBlockView"

    member_order = [
        "video",
        "player_settings"
    ]

    video = schema.Reference(
        type = Publishable,
        required = True,
        relation_constraints = {"resource_type": "video"},
        related_end = schema.Collection(),
        invalidates_cache = True,
        member_group = "content"
    )

    player_settings = schema.Reference(
        type = VideoPlayerSettings,
        required = True,
        related_end = schema.Collection(),
        invalidates_cache = True,
        member_group = "content"
    )

    def get_block_image(self):
        return self.video

    def init_view(self, view):
        Block.init_view(self, view)
        view.video = self.video
        view.player_settings = self.player_settings
        view.depends_on(self.video)

