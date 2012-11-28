#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block


class Slot(schema.Collection):

    def __init__(self, *args, **kwargs):

        if "items" not in kwargs:
            kwargs["items"] = schema.Reference(type = Block)

        kwargs["related_end"] = schema.Collection()
        kwargs["cascade_delete"] = True
        kwargs.setdefault("listable", False)
        kwargs.setdefault("searchable", False)
        kwargs.setdefault("member_group", "content")
        schema.Collection.__init__(self, *args, **kwargs)

