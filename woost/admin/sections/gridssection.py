#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Grid
from .crud import CRUD


class GridsSection(CRUD):
    model = Grid

