#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element, first_last_classes
from woost.extensions.blocks.utils import create_block_views


class BlockList(Element):

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        first_last_classes(self)

    def _build(self):
        self.blocks_container = self

    def _ready(self):
        Element._ready(self)
        self._fill_blocks()

    def _fill_blocks(self):
        if self.blocks:
            if self.tag in ("ul", "ol"):
                for block_view in create_block_views(self.blocks):
                    entry = Element("li")
                    entry.append(block_view)
                    self.blocks_container.append(entry)
            else:
                for block_view in create_block_views(self.blocks):
                    self.blocks_container.append(block_view)

