#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Site
from woost.extensions.blocks.block import Block


Site.add_member(
    schema.Collection(
        "common_blocks",
        items = schema.Reference(type = Block),
        related_end = schema.Reference()
    )
)

