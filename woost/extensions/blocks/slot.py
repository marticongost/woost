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


# This method is defined here to avoid an import cycle
def descend_blocks(self, include_self = False):

    if include_self:
        yield self

    for member in self.__class__.members().itervalues():
        if isinstance(member, Slot):
            children = self.get(member)
            if children is not None:
                for child in children:
                    for descendant in child.descend_blocks(True):
                        yield descendant

Block.descend_blocks = descend_blocks

