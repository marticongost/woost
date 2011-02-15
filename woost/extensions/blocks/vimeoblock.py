#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block
from woost.extensions.vimeo.video import VimeoVideo


class VimeoBlock(Block):

    instantiable = True
    view_class = "woost.extensions.vimeo.VimeoPlayer"


    video = schema.Reference(
        required = True,
        type = VimeoVideo,
        related_end = schema.Collection(),
        member_group = "content",
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.video = self.video

