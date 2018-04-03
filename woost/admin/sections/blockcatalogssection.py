#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import BlocksCatalog
from .crud import CRUD


class BlockCatalogsSection(CRUD):
    model = BlocksCatalog

