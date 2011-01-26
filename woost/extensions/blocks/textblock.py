#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from cocktail.modeling import getter
from woost.extensions.blocks.block import Block


class TextBlock(Block):

    instantiable = True

    text = schema.String(
        required = True,
        member_group = "content",
        edit_control = "cocktail.html.TextArea"
    )

    @getter
    def available_templates(self):
        return [
            "woost.extensions.blocks.TextBlockView"
        ]

