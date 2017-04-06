#-*- coding: utf-8 -*-
u"""

.. moduleauthor::  <>
"""
from woost.models import Item
from .newsletter import Newsletter

base_allows_block_type = getattr(Item, "allows_block_type", None)

def allows_block_type(self, block_type):
    if issubclass(block_type, Newsletter.allowed_block_types):
        return False
    else:
        if base_allows_block_type:
            return base_allows_block_type(self, block_type)
        else:
            return True

Item.allows_block_type = allows_block_type

