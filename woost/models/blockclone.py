#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from .item import Item
from .block import Block


class BlockClone(Block):

    instantiable = False

    members_order = [
        "source_block"
    ]

    source_block = schema.Reference(
        type = "woost.models.Block",
        bidirectional = True,
        related_key = "clones",
        required = True,
        text_search = True,
        editable = schema.READ_ONLY,
        member_group = "content"
    )

    def is_published(self):
        return Block.is_published(self) and self.source_block.is_published()

    def create_view(self):
        view = self.source_block.create_view()
        self.init_view(view)
        self.customize_view(view)
        return view

    def add_view_dependencies(self, view):
        Block.add_view_dependencies(self, view)
        self.source_block.add_view_dependencies(view)

