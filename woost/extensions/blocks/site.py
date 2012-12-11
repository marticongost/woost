#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Site
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.slot import Slot


Site.add_member(Slot("common_blocks"))

