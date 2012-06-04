#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block


class ContainerBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.BlockList"

    blocks = schema.Collection(
        items = schema.Reference(type = Block),
        related_end = schema.Collection(),
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.blocks = self.blocks
        return view

