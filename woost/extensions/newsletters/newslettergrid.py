#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.html import Element, templates
from woost.models.blockutils import create_block_views
from woost.extensions.newsletters import NewslettersExtension


class NewsletterGrid(Element):

    tag = "table"
    items = None
    content_appearence = None
    content_view_factory = None
    content_image_factory = None
    blocks = None
    container = None
    slot = None
    width = None
    base_spacing = None
    spacing = 0
    column_count = 1
    column_width = None
    fix_children_width = True
    vertical_border_style = None
    horizontal_border_style = None

    def _build(self):
        self["cellpadding"] = 0
        self["cellspacing"] = 0
        self["border"] = 0
        self.content_container = self

    def _ready(self):
        Element._ready(self)

        self.is_single_column = (self.column_count == 1)

        if self.column_width is None and self.width and self.column_count:
            width = self.width - self.spacing * (self.column_count - 1)

            if self["cellspacing"]:
                width -= int(self["cellspacing"]) * 2

            if self["cellpadding"]:
                width -= int(self["cellpadding"]) * 2

            self.column_width = width / self.column_count

        if self.blocks is None:
            if self.container is not None and self.slot is not None:
                if isinstance(self.slot, basestring):
                    slot = self.container.__class__.get_member(self.slot)
                else:
                    slot = self.slot

                if slot:
                    self.depends_on(self.container, slot.cache_part)
                    self.blocks = getattr(self.container, slot.name, None)

        child_views = None

        if self.blocks:
            child_views = create_block_views(
                self.blocks,
                content_appearence = self.content_appearence
            )
        elif self.items and self.content_view_factory:
            child_views = (
                self.content_view_factory.create_view(
                    item,
                    image_factory = self.content_image_factory
                )
                for item in self.items
            )

        if child_views is not None:
            visible_views = []
            for child_view in child_views:
                self._init_child_view(child_view)
                child_view.width = self.column_width
                child_view.ready()
                if child_view.visible:
                    visible_views.append(child_view)
            child_views = visible_views

        if child_views:
            self._fill_content(child_views)
        else:
            self.visible = False

    def _fill_content(self, child_views):

        column_index = 0
        row_index = 0
        row = None
        suppress_spacing = False

        for child_view in child_views:

            # Separators
            if getattr(child_view, "is_separator", False):
                self.content_container.append(child_view)
                row = None
                column_index = 0
                supress_spacing = True
                continue

            if row is None:
                if suppress_spacing:
                    suppress_spacing = False
                elif (
                    row_index
                    and (self.spacing or self.horizontal_border_style)
                ):
                    self.content_container.append(
                        self._create_vertical_separator()
                    )

                row = Element("tr")
                self.content_container.append(row)

            if column_index and (
                self.spacing
                or self.vertical_border_style
            ):
                row.append(self._create_horizontal_separator())

            cell = Element("td")
            cell.add_class("newsletter_grid_cell")
            if self.fix_children_width:
                cell["width"] = self.column_width
            cell.append(child_view)
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

    def _init_child_view(self, child_view):
        NewslettersExtension.inheriting_view_attributes(
            parent_view = self,
            child_view = child_view
        )

