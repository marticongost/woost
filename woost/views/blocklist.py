#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element, first_last_classes


class BlockList(Element):

    __wrap = None
    blocks = None
    container = None
    slot = None
    hide_if_empty = False
    wrap_dl_entries = False

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        first_last_classes(self)

    def _build(self):
        self.blocks_container = self

    def _ready(self):
        Element._ready(self)

        if self.blocks is None:
            if self.container is not None and self.slot is not None:
                if isinstance(self.slot, basestring):
                    slot = self.container.__class__.get_member(self.slot)
                else:
                    slot = self.slot

                if slot:
                    self.depends_on(self.container, slot.cache_part)
                    self.blocks = self.get_blocks(self.container, slot)

        if self.tag in ("ul", "ol"):
            self.__wrap = self.wrap_with_list_item
        elif self.tag == "table":
            self.__wrap = self.wrap_with_table_row
        elif self.wrap_dl_entries and self.tag == "dl":
            self.__wrap = self.wrap_with_dl_row

        self._fill_blocks()

    def get_blocks(self, container, slot):
        return getattr(container, slot.name, None)

    def _fill_blocks(self):
        has_visible_blocks = False

        if self.blocks:
            for block in self.blocks:
                block.add_view_dependencies(self)
                if block.is_published():
                    has_visible_blocks = True
                    block_view = self.create_block_view(block)
                    self._insert_block_view(block_view)

        if self.hide_if_empty and not has_visible_blocks:
            self.visible = False

    def create_block_view(self, block):
        return block.create_view()

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

    def wrap_with_dl_row(self, block_view):
        entry = Element()
        entry.add_class("dl_entry")
        entry.append(block_view)
        return entry

