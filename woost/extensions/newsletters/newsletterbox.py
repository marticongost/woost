#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail import schema
from woost.models import Block, Slot
from woost.extensions.newsletters.members import (
    NewsletterContentLayout,
    NewsletterContentImageSize,
    NewsletterContentAppearence,
    Spacing
)


class NewsletterBox(Block):

    instantiable = True

    type_group = "blocks.newsletter"

    members_order = [
        "column_count",
        "view_class",
        "content_layout",
        "content_image_size",
        "content_appearence",
        "spacing_factor",
        "blocks"
    ]

    column_count = schema.Integer(
        required = True,
        min = 1,
        default = 1,
        member_group = "content"
    )

    view_class = schema.String(
        shadows_attribute = True,
        required = True,
        default = "woost.extensions.newsletters.NewsletterBoxView",
        enumeration = [
            "woost.extensions.newsletters.NewsletterBoxView"
        ],
        edit_control = "cocktail.html.RadioSelector",
        member_group = "content"
    )

    content_layout = NewsletterContentLayout(
        member_group = "content"
    )

    content_image_size = NewsletterContentImageSize(
        member_group = "content"
    )

    content_appearence = NewsletterContentAppearence(
        member_group = "content"
    )

    spacing_factor = Spacing(
        required = True,
        member_group = "content"
    )

    blocks = Slot()

    def init_view(self, view):
        Block.init_view(self, view)
        view.column_count = self.column_count
        view.blocks = self.blocks
        view.content_layout = self.content_layout
        view.content_image_size = self.content_image_size
        view.content_appearence = self.content_appearence
        view.spacing_factor = self.spacing_factor
        return view

