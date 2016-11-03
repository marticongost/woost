#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from .slot import Slot
from .block import Block
from .file import File
from .blockimagefactoryreference import BlockImageFactoryReference


class ContainerBlock(Block):

    instantiable = True
    type_group = "blocks.layout"
    views = ["woost.views.ContainerBlockView"]

    members_order = [
        "list_type",
        "background_image",
        "background_image_factory",
        "blocks"
    ]

    list_type = schema.String(
        required = True,
        default = "div",
        enumeration = [
            "div",
            "ul",
            "ol",
            "dl"
        ],
        member_group = "content"
    )

    background_image = schema.Reference(
        type = File,
        related_end = schema.Collection(),
        relation_constraints = {"resource_type": "image"},
        member_group = "content"
    )

    background_image_factory = BlockImageFactoryReference(
        member_group = "content"
    )

    blocks = Slot()

    def init_view(self, view):
        Block.init_view(self, view)
        view.blocks_list.tag = self.list_type
        view.blocks = self.blocks

        if self.background_image:
            view.background_image = self.background_image

        if self.background_image_factory:
            view.background_image_factory = self.background_image_factory

        return view

    def get_block_proxy(self, view):
        if self.element_type == "dd":
            return view.blocks_list
        return view

