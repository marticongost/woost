#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .path import ascend
from woost.models import Block

@ascend.implementation_for(Block)
def ascend_block(self):
    block = self
    while True:
        location = block.get_block_location()
        if location:
            block = location[0]
            yield block
        else:
            break

