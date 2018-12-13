#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from cocktail.iteration import first
from .rendering import ImageFactory

def _block_image_factories_enumeration(ctx):
    return list(
        ImageFactory.select(
            ImageFactory.applicable_to_blocks.equal(True)
        )
    )


class BlockImageFactoryReference(schema.Reference):

    def __init__(self, *args, **kwargs):

        kwargs.setdefault("type", ImageFactory)
        kwargs.setdefault("enumeration", _block_image_factories_enumeration)
        kwargs.setdefault("edit_control", "cocktail.html.DropdownSelector")

        if "bidirectional" not in kwargs and "related_end" not in kwargs:
            kwargs["related_end"] = schema.Collection()

        schema.Reference.__init__(self, *args, **kwargs)

