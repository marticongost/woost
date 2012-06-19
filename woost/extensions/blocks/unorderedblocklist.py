#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element, first_last_classes
from woost.extensions.blocks.blocklist import BlockList


class UnorderedBlockList(BlockList):

    def _build(self):
        self.blocks_container = Element("ul")
        self.append(self.blocks_container)
        first_last_classes(self.blocks_container)

    def create_entry(self, block):
        block_view = BlockList.create_entry(self, block)
        if block_view:
            entry = Element("li")
            entry.append(block_view)
            return entry

