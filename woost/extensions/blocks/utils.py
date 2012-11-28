#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.slot import Slot

def create_block_views(blocks):
    for block in blocks:
        if block.is_published():
            view = block.create_view()
            if view is not None:
                yield view

def find_blocks(obj, slots = None):

    if isinstance(obj, Block):
        yield obj

    if slots is None:
        slots = (member
                for member in obj.__class__.members().itervalues()
                if isinstance(member, Slot))

    for slot in slots:
        blocks = obj.get(slot)
        if blocks is not None:
            for block in blocks:
                for descendant in find_blocks(block):
                    yield descendant

