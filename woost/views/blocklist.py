#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element, first_last_classes
from woost.models.blockutils import create_block_views


class BlockList(Element):

    __wrap = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        first_last_classes(self)

    def _build(self):
        self.blocks_container = self

    def _ready(self):
        Element._ready(self)

        if self.tag in ("ul", "ol"):
            self.__wrap = self.wrap_with_list_item
        elif self.tag == "table":
            self.__wrap = self.wrap_with_table_row

        self._fill_blocks()

    def _fill_blocks(self):
        if self.blocks:
            for block_view in create_block_views(self.blocks):
                self._insert_block_view(block_view)

    def _insert_block_view(self, block_view):
        if self.__wrap:
            entry = self.__wrap(block_view)
            self.blocks_container.append(entry)
        else:
            self.blocks_container.append(block_view)

    def wrap_with_list_item(self, block_view):
        entry = Element("li")
        entry.append(block_view)
        return entry

    def wrap_with_table_row(self, block_view):
        row = Element("tr")
        row.cell = Element("td")
        row.cell.append(block_view)
        row.append(row.cell)
        return row

