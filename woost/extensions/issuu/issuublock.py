#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.models import Configuration
from woost.extensions.blocks.block import Block
from woost.extensions.issuu.issuudocument import IssuuDocument


class IssuuBlock(Block):

    instantiable = True
    views = ["woost.extensions.issuu.IssuuBlockView"]
    block_display = "woost.extensions.issuu.IssuuBlockDisplay"

    members_order = [
        "issuu_document",
        "width",
        "height"
    ]

    issuu_document = schema.Reference(
        type = IssuuDocument,
        required = True,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "content"
    )

    width = schema.Integer(
        listed_by_default = False,
        member_group = "content"
    )

    height = schema.Integer(
        listed_by_default = False,
        member_group = "content"
    )

