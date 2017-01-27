#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from .slot import Slot
from .block import Block
from .file import File
from .publishable import Publishable
from .blockimagefactoryreference import BlockImageFactoryReference


class ContainerBlock(Block):

    instantiable = True
    type_group = "blocks.layout"
    views = ["woost.views.ContainerBlockView"]

    groups_order = ["content", "background", "link"] + Block.groups_order[1:]

    members_order = [
        "list_type",
        "background_image",
        "background_image_factory",
        "link_destination",
        "link_parameters",
        "link_opens_in_new_window",
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
        member_group = "background"
    )

    background_image_factory = BlockImageFactoryReference(
        member_group = "background"
    )

    link_destination = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        member_group = "link",
        invalidates_cache = True
    )

    link_parameters = schema.String(
        edit_control = "cocktail.html.TextArea",
        text_search = False,
        member_group = "link"
    )

    link_opens_in_new_window = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "link"
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

        if self.link_destination is not None:
            view.link_destination = self.link_destination

        if self.link_parameters is not None:
            view.link_parameters = self.link_parameters

        if self.link_opens_in_new_window is not None:
            view.link_opens_in_new_window = self.link_opens_in_new_window

        return view

    def get_block_proxy(self, view):
        if self.element_type == "dd":
            return view.blocks_list
        return view

