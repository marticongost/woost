#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element


class BlockList(Element):

    def _build(self):
        self.blocks_container = self

    def _ready(self):
        Element._ready(self)
        self._fill_blocks()

    def _fill_blocks(self):
        if self.blocks:
            for block in self.blocks:
                if block.is_published():
                    block_view = self.create_entry(block)
                    if block_view is not None:
                        self.blocks_container.append(block_view)

    def create_entry(self, block):
        return block.create_view()

