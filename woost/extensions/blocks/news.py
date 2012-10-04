#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import News
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.slot import Slot

# Replace the News.body text member with a list of blocks
News.body.visible = False

News.add_member(Slot("blocks"))

