#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block


class ContainerBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.ContainerBlockView"

    members_order = [
        "element_type",
        "list_type"
    ]

    element_type = schema.String(
        required = True,
        default = "div",
        enumeration = [
            "div",
            "section",
            "article",
            "details",
            "aside",
            "header",
            "footer",
            "nav",
            "dd"
        ],
        member_group = "content"
    )

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

    blocks = schema.Collection(
        items = schema.Reference(type = Block),
        related_end = schema.Collection(),
        cascade_delete = True,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)

        if self.element_type == "dd":
            view.tag = None
            view.blocks_list.tag = "dd"
        else:
            view.tag = self.element_type

        view.blocks_list.tag = self.list_type
        view.blocks = self.blocks
        return view

    def get_block_proxy(self, view):
        if self.element_type == "dd":
            return view.blocks_list
        return view

