#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block


class ContainerBlock(Block):

    instantiable = True

    blocks = schema.Collection(
        items = schema.Reference(type = Block),
        related_end = schema.Collection(),
        cascade_delete = True,
        member_group = "content"
    )

    view_class = schema.String(
        shadows_attribute = True,
        required = True,
        default = "woost.extensions.blocks.BlockList",
        enumeration = [
            "woost.extensions.blocks.BlockList",
            "woost.extensions.blocks.UnorderedBlockList",
            "woost.extensions.blocks.OrderedBlockList"
        ],
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.blocks = self.blocks
        return view

