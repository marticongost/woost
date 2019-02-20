#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import BlocksCatalog
from .crud import CRUD


class BlockCatalogsSection(CRUD):
    model = BlocksCatalog

