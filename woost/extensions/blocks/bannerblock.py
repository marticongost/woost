#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from cocktail.modeling import getter
from woost.models import File, Publishable
from woost.extensions.blocks.block import Block


class BannerBlock(Block):

    instantiable = True

    text = schema.String(
        member_group = "content"
    )

    target = schema.Reference(
        required = True,
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

    @getter
    def available_templates(self):
        return [
            "woost.extensions.blocks.BannerBlockView"
        ]

