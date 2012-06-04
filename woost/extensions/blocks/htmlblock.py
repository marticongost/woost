#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.models import Publishable
from woost.extensions.blocks.block import Block


class HTMLBlock(Block):

    instantiable = True
    view_class = "cocktail.html.Element"

    html = schema.CodeBlock(
        required = True,
        language = "html",
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)        
        view.append(self.html)

