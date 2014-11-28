#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from decimal import Decimal
from cocktail import schema
from woost.models import Block
from woost.extensions.newsletters.members import Spacing, BorderStyle


class NewsletterSeparator(Block):

    type_group = "blocks.newsletter"
    view_class = "woost.extensions.newsletters.VerticalSeparator"

    height_factor = Spacing(
        default = Decimal("1"),
        required = True,
        enumeration = None,
        edit_control = "cocktail.html.TextBox",
        member_group = "content"
    )

    border_style = BorderStyle(
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.height_factor = self.height_factor
        view.border_style = self.border_style

    def get_block_proxy(self, view):
        return view.vertical_separator_top_cell

