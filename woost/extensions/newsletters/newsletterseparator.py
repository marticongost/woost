#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from decimal import Decimal
from cocktail import schema
from woost.models import Block
from woost.extensions.newsletters.members import Spacing


class NewsletterSeparator(Block):

    type_group = "blocks.newsletter"
    view_class = "woost.extensions.newsletters.NewsletterSeparator"

    spacing_factor = Spacing(
        default = Decimal("1"),
        required = True,
        enumeration = None,
        edit_control = "cocktail.html.TextBox",
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.spacing_factor = self.spacing_factor

