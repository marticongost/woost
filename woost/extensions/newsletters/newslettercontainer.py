#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from decimal import Decimal
from cocktail import schema
from woost.models import Block, Slot
from woost.extensions.newsletters.members import (
    HeadingPosition,
    NewsletterContentLayout,
    NewsletterContentImageSize,
    NewsletterImageFactory,
    Spacing,
    LinkStyle,
    BorderStyle
)


class NewsletterContainer(Block):

    instantiable = False

    type_group = "blocks.newsletter"

    members_order = [
        "heading_position",
        "content_layout",
        "content_image_size",
        "content_image_factory",
        "image_spacing",
        "link_style",
        "spacing_factor",
        "vertical_border_style",
        "horizontal_border_style"
    ]

    column_count = schema.Integer(
        required = True,
        min = 1,
        default = 1,
        member_group = "content"
    )

    heading_position = HeadingPosition(
        member_group = "content.entries"
    )

    content_layout = NewsletterContentLayout(
        member_group = "content.entries"
    )

    content_image_size = NewsletterContentImageSize(
        member_group = "content.entries"
    )

    content_image_factory = NewsletterImageFactory(        
        member_group = "content.entries"    
    )

    image_spacing = Spacing(
        member_group = "content.entries"
    )

    link_style = LinkStyle(
        member_group = "content.entries"
    )

    spacing_factor = Spacing(
        required = True,
        default = Decimal("1.0"),
        member_group = "content.separation"
    )

    vertical_border_style = BorderStyle(
        member_group = "content.separation"
    )

    horizontal_border_style = BorderStyle(
        member_group = "content.separation"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.column_count = self.column_count
        view.heading_position = self.heading_position
        view.content_layout = self.content_layout
        view.content_image_size = self.content_image_size
        view.content_image_factory = self.content_image_factory
        view.image_spacing = self.image_spacing
        view.spacing_factor = self.spacing_factor
        view.link_style = self.link_style
        view.vertical_border_style = self.vertical_border_style
        view.horizontal_border_style = self.horizontal_border_style
        return view

