#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from decimal import Decimal
from cocktail import schema
from woost.models import Block, Slot
from woost.extensions.newsletters.members import (
    NewsletterContentLayout,
    NewsletterContentImageSize,
    NewsletterContentAppearence,
    Spacing,
    LinkStyle,
    BorderStyle
)


class NewsletterBox(Block):

    instantiable = True

    type_group = "blocks.newsletter"

    members_order = [
        "column_count",
        "view_class",
        "content_layout",
        "content_image_size",
        "image_spacing",
        "link_style",
        "content_appearence",
        "spacing_factor",
        "vertical_border_style",
        "horizontal_border_style",
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

    image_spacing = Spacing(
        member_group = "content"
    )

    link_style = LinkStyle(
        member_group = "content"
    )

    content_appearence = NewsletterContentAppearence(
        member_group = "content"
    )

    spacing_factor = Spacing(
        required = True,
        default = Decimal("1.0"),
        member_group = "content"
    )

    vertical_border_style = BorderStyle(
        member_group = "content"
    )

    horizontal_border_style = BorderStyle(
        member_group = "content"
    )

    blocks = Slot()

    def init_view(self, view):
        Block.init_view(self, view)
        view.column_count = self.column_count
        view.blocks = self.blocks
        view.content_layout = self.content_layout
        view.content_image_size = self.content_image_size
        view.image_spacing = self.image_spacing
        view.content_appearence = self.content_appearence
        view.spacing_factor = self.spacing_factor
        view.link_style = self.link_style
        view.vertical_border_style = self.vertical_border_style
        view.horizontal_border_style = self.horizontal_border_style
        return view

