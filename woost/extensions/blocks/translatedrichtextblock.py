#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from cocktail.modeling import getter
from woost.extensions.blocks.block import Block


class TranslatedRichTextBlock(Block):

    instantiable = True
    view_class = "cocktail.html.Element"

    text = schema.String(
        required = True,
        edit_control = "woost.views.RichTextEditor",
        translated = True,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)        
        view.append(self.text)

