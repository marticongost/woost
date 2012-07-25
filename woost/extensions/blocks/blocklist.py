#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element
from woost.extensions.blocks.utils import create_block_views


class BlockList(Element):

    def _build(self):
        self.blocks_container = self

    def _ready(self):
        Element._ready(self)
        self._fill_blocks()

    def _fill_blocks(self):
        if self.blocks:
            create_entry = getattr(
                self, 
                "create_%s_entry" % self.tag,
                self.create_entry
            )

            for block_view in create_block_views(self.blocks):
                self.blocks_container.append(block_view)

    def create_entry(self, block):
        return block.create_view()
        
    def create_ul_entry(self, block):
        block_view = self.create_entry(block)
        if block_view:
            entry = Element("li")
            entry.append(block_view)
            return entry

    create_ol_entry = create_ul_entry

