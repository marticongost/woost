#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element


class BlockList(Element):

    def _ready(self):
        Element._ready(self)
        if self.blocks:
            for block in self.blocks:
                if block.is_published():
                    view = block.create_view()
                    if view is not None:
                        self.append(view)

