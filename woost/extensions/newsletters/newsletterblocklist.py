#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.html import Element
from woost.models.blockutils import create_block_views
from woost.extensions.newsletters import NewslettersExtension


class NewsletterBlockList(Element):

    tag = "table"
    blocks = None
    container = None
    slot = None
    width = None
    base_spacing = None
    spacing = None
    column_count = 1

    def _build(self):
        self["cellpadding"] = 0
        self["cellspacing"] = 0
        self["border"] = 0
        self.blocks_container = self

    def _ready(self):
        self["width"] = self.width
        Element._ready(self)

        if self.blocks is None:
            if self.container is not None and self.slot is not None:
                if isinstance(self.slot, basestring):
                    slot = self.container.__class__.get_member(self.slot)
                else:
                    slot = self.slot

                if slot:
                    self.depends_on(self.container, slot.cache_part)
                    self.blocks = getattr(self.container, slot.name, None)

        self._fill_blocks()

    def _fill_blocks(self):

        self.is_single_column = (self.column_count == 1)

        if self.blocks:
            if self.width:
                width = self.width - self.spacing * (self.column_count - 1)

                if self["cellspacing"]:
                    width -= int(self["cellspacing"]) * 2

                if self["cellpadding"]:
                    width -= int(self["cellpadding"]) * 2

                column_width = width / self.column_count

            column_index = 0
            row_index = 0
            row = None

            for block_view in create_block_views(self.blocks):

                self._init_block_view(block_view)
                block_view.width = column_width
                block_view.ready()

                if not block_view.visible:
                    continue

                if row is None:
                    if row_index:
                        self.blocks_container.append(self._create_vspace())

                    row = Element("tr")
                    self.blocks_container.append(row)

                if column_index:
                    row.append(self._create_hspace())

                cell = Element("td")
                cell["width"] = column_width
                cell.append(block_view)
                row.append(cell)

                column_index += 1
                if column_index == self.column_count:
                    column_index = 0
                    row = None
                    row_index += 1

    def _create_vspace(self):
        row = Element("tr")
        cell = Element("td")
        cell.add_class("vspace_cell")
        cell["colspan"] = self.column_count
        cell["height"] = self.spacing
        row.append(cell)
        return row

    def _create_hspace(self):
        cell = Element("td")
        cell.add_class("hspace_cell")
        cell["width"] = self.spacing
        return cell

    def create_block_view(block_list, block):
        return block.create_view(inherited_appearence = self.content_appearence)

    def _init_block_view(self, block_view):
        NewslettersExtension.inheriting_view_attributes(
            parent_view = self,
            child_view = block_view
        )

