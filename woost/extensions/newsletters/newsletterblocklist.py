#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.html import Element, templates
from woost.models.blockutils import create_block_views
from woost.extensions.newsletters import NewslettersExtension


class NewsletterBlockList(Element):

    tag = "table"
    blocks = None
    container = None
    slot = None
    width = None
    base_spacing = None
    spacing = 0
    column_count = 1
    fix_children_width = True
    vertical_border_style = None
    horizontal_border_style = None

    def _build(self):
        self["cellpadding"] = 0
        self["cellspacing"] = 0
        self["border"] = 0
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
            suppress_spacing = False

            for block_view in create_block_views(self.blocks):

                self._init_block_view(block_view)
                block_view.width = column_width
                block_view.ready()

                if not block_view.visible:
                    continue

                # Separators
                if getattr(block_view, "is_separator", False):
                    self.blocks_container.append(block_view)
                    row = None
                    column_index = 0
                    supress_spacing = True
                    continue

                if row is None:
                    if suppress_spacing:
                        suppress_spacing = False
                    elif (
                        row_index
                        and (
                            self.spacing
                            or self.horizontal_border_style
                        )
                    ):
                        self.blocks_container.append(
                            self._create_vertical_separator()
                        )

                    row = Element("tr")
                    self.blocks_container.append(row)

                if column_index and (
                    self.spacing
                    or self.vertical_border_style
                ):
                    row.append(self._create_horizontal_separator())

                cell = Element("td")
                cell.add_class("newsletter_block_list_cell")
                if self.fix_children_width:
                    cell["width"] = column_width
                cell.append(block_view)
                row.append(cell)

                column_index += 1
                if column_index == self.column_count:
                    column_index = 0
                    row = None
                    row_index += 1

    def _create_vertical_separator(self):

        sep = templates.new("woost.extensions.newsletters.VerticalSeparator")

        sep.width = self.width
        sep.height = self.spacing
        sep.border_style = self.horizontal_border_style
        
        columns = self.column_count
        if self.vertical_border_style:
            columns += (columns - 1) * 2
        elif self.spacing:
            columns += columns - 1

        sep.parent_column_count = columns
        return sep

    def _create_horizontal_separator(self):        
        sep = templates.new("woost.extensions.newsletters.HorizontalSeparator")
        sep.width = self.spacing
        sep.border_style = self.vertical_border_style
        return sep

    def create_block_view(block_list, block):
        return block.create_view(inherited_appearence = self.content_appearence)

    def _init_block_view(self, block_view):
        NewslettersExtension.inheriting_view_attributes(
            parent_view = self,
            child_view = block_view
        )

