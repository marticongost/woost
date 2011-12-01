#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.models import File, Publishable
from woost.extensions.blocks.block import Block


class BannerBlock(Block):

    instantiable = True
    tag = "a"
    view_class = "woost.extensions.blocks.Banner"

    members_order = [
        "target",
        "image",
        "text",
        "label_displayed"
    ]

    image = schema.Reference(
        type = File,
        integral = True,
        related_end = schema.Collection(),
        member_group = "content"
    )

    target = schema.Reference(
        type = Publishable,
        required = True,
        related_end = schema.Collection(cascade_delete = True),
        member_group = "content"
    )

    text = schema.String(
        translated = True,
        member_group = "content"
    )

    label_displayed = schema.Boolean(
        default = True,
        required = True,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.image = self.image
        view.target = self.target
        view.text = self.text
        view.label_displayed = self.label_displayed
        from cocktail.styled import styled
        print styled(view, "green"), view.label_displayed

