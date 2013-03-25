#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from cocktail.controllers import request_property
from woost.models import Publishable, VideoPlayerSettings
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.elementtype import ElementType


class VideoBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.VideoBlockView"

    member_order = ["element_type", "video", "player_settings"]

    element_type = ElementType(
        member_group = "content"
    )   

    video = schema.Reference(
        type = Publishable,
        required = True,
        relation_constraints = {"resource_type": "video"},
        related_end = schema.Collection(),
        member_group = "content"
    )

    player_settings = schema.Reference(
        type = VideoPlayerSettings,
        required = True,
        related_end = schema.Collection(),
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.tag = self.element_type
        view.video = self.video
        view.player_settings = self.player_settings

