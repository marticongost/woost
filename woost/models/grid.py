#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from .item import Item


class Grid(Item):

    type_group = "customization"

    members_order = [
        "title",
        "column_count",
        "sizes"
    ]

    title = schema.String(
        required = True,
        translated = True,
        descriptive = True,
        indexed = True,
        unique = True
    )

    column_count = schema.Integer(
        required = True,
        default = 12
    )

    sizes = schema.Collection(
        items = "woost.models.GridSize",
        bidirectional = True,
        integral = True,
        listed_by_default = True
    )

    def get_sass_code(self):

        size_defs = []

        for size in self.sizes:
            geometry = {}

            if size.min_width is not None:
                geometry["min-width"] = size.min_width

            if size.column_width is not None:
                geometry["col-width"] = size.column_width

            if size.column_spacing is not None:
                geometry["col-spacing"] = size.column_spacing

            size_defs.append(
                "%s: (%s)" % (
                    size.identifier,
                    ", ".join(
                        ("%s:%dpx" % prop) for prop in geometry.iteritems()
                    )
                )
            )

        return "@include define_grid((%s), $col-count: %d);" % (
            ", ".join(size_defs),
            self.column_count
        )


class GridSize(Item):

    visible_from_root = False
    type_group = "customization"

    members_order = [
        "grid",
        "identifier",
        "min_width",
        "column_width",
        "column_spacing"
    ]

    grid = schema.Reference(
        type = "woost.models.Grid",
        bidirectional = True
    )

    identifier = schema.String(
        required = True,
        descriptive = True
    )

    min_width = schema.Integer(
        min = 0
    )

    column_width = schema.Integer(
        min = 0
    )

    column_spacing = schema.Integer(
        min = 0
    )

