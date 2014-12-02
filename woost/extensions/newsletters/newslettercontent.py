#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.translations import  translations
from cocktail import schema
from woost.models import Block, Publishable, File
from woost.extensions.newsletters.members import (
    HeadingPosition,
    NewsletterContentLayout,
    NewsletterContentImageSize,
    NewsletterContentAppearence,
    NewsletterImageFactory,
    Spacing,
    LinkStyle
)


class NewsletterContent(Block):

    instantiable = True
    block_display = "woost.extensions.newsletters.NewsletterContentDisplay"
    type_group = "blocks.newsletter"

    members_order = [
        "heading_position",
        "text",
        "link",
        "image",
        "image_size",
        "image_factory",
        "image_spacing",
        "link_style",
        "layout",
        "appearence"
    ]

    heading_position = HeadingPosition(
        after_member = "heading_type",
        member_group = "content"
    )

    text = schema.HTML(
        edit_control = "woost.extensions.newsletters.NewsletterRichTextEditor",
        translated = True,
        member_group = "content"
    )

    link = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        member_group = "content"
    )

    image = schema.Reference(
        type = File,
        related_end = schema.Collection(),
        relation_constraints = [File.resource_type.equal("image")],
        member_group = "content"
    )

    layout = NewsletterContentLayout(
        member_group = "content"
    )
    
    image_size = NewsletterContentImageSize(
        member_group = "content"
    )

    image_factory = NewsletterImageFactory(
        member_group = "content"
    )

    image_spacing = Spacing(
        member_group = "content"
    )

    link_style = LinkStyle(
        member_group = "content"
    )

    appearence = NewsletterContentAppearence(
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.heading_position = self.heading_position
        view.text = self.text
        view.link = self.link
        view.image = self.image
        view.content_layout = self.layout
        view.content_image_size = self.image_size
        view.content_image_factory = self.image_factory
        view.image_spacing = self.image_spacing
        view.link_style = self.link_style

    def get_view_class(self, inherited_appearence = None, **kwargs):
        return (
            self.appearence
            or inherited_appearence
            or NewsletterContentAppearence.enumeration[0]
        )

