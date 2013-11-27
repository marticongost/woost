#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import TypeGroup

block_type_groups = TypeGroup("blocks", [
    TypeGroup("blocks.content"),
    TypeGroup("blocks.layout"),
    TypeGroup("blocks.listings"),
    TypeGroup("blocks.social"),
    TypeGroup("blocks.forms"),
    TypeGroup("blocks.custom")
])

