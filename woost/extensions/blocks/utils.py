#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

def create_block_views(blocks):
    for block in blocks:
        if block.is_published():
            view = block.create_view()
            if view is not None:
                yield view

