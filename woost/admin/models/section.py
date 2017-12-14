#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Item, File


class Section(Item):

    members_order = [
        "title",
        "path",
        "image",
        "ui_node",
        "ui_component",
        "data",
        "parent",
        "children"
    ]

    title = schema.String(
        required = True,
        descriptive = True,
        translated = True
    )

    path = schema.String(
        required = True
    )

    image = schema.Reference(
        type = File,
        related_end = schema.Collection(),
        relation_constraints = {"resource_type": "image"},
        integral = True
    )

    ui_node = schema.String(
        required = True,
        default = "woost.admin.nodes.Section"
    )

    ui_component = schema.String()

    data = schema.JSON()

    parent = schema.Reference(
        type = "woost.admin.models.Section",
        bidirectional = True
    )

    children = schema.Collection(
        items = "woost.admin.models.Section",
        bidirectional = True,
        integral = True
    )

