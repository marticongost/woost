#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.translations import  translations
from cocktail import schema
from woost.models import Block, Publishable, File
from woost.extensions.newsletters.members import (
    NewsletterContentLayout,
    NewsletterContentImageSize,
    NewsletterContentAppearence
)


class NewsletterContent(Block):

    instantiable = True
    block_display = "woost.extensions.newsletters.NewsletterContentDisplay"
    type_group = "blocks.newsletter"

    members_order = [
        "text",
        "link",
        "image",
        "image_size",
        "layout",
        "appearence"
    ]

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

    appearence = NewsletterContentAppearence(
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.text = self.text
        view.link = self.link
        view.image = self.image
        view.content_layout = self.layout
        view.content_image_size = self.image_size

    def get_view_class(self, inherited_appearence = None, **kwargs):
        return (
            self.appearence
            or inherited_appearence
            or NewsletterContentAppearence.appearences[0]
        )

