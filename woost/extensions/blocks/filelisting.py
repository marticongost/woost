#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.schema.expressions import Self
from woost.models import File
from woost.models.rendering import ImageFactory
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.elementtype import ElementType


class FileListing(Block):

    instantiable = False
    type_group = "blocks.listings"
    view_class = "woost.views.FileListing"

    groups_order = list(Block.groups_order)
    groups_order.insert(groups_order.index("content") + 1, "listing")

    members_order = [
        "files",
        "listing_order",
        "links_open_in_new_window",
        "image_factory"
    ]

    element_type = ElementType(
        member_group = "content"
    )

    files = schema.Collection(
        items = schema.Reference(type = File),
        related_end = schema.Collection(),
        member_group = "listing"
    )

    listing_order = schema.String(
        default = "arbitrary",
        enumeration = ["arbitrary", "title", "-last_update_time"],
        member_group = "listing"
    )

    links_open_in_new_window = schema.Boolean(
        required = True,
        default = False,
        member_group = "listing"
    )

    image_factory = schema.Reference(
        type = ImageFactory,
        related_end = schema.Collection(),
        required = True,
        member_group = "listing"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.tag = self.element_type
        view.files = self.select_files()
        view.links_open_in_new_window = self.links_open_in_new_window
        view.image_factory = self.image_factory

    def select_files(self):
        files = File.select_accessible()
        files.base_collection = self.files

        if self.listing_order != "arbitrary":
            files.add_order(self.listing_order)

        return files

