#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models.rendering import Renderer
from .crud import CRUD


class RenderersSection(CRUD):
    model = Renderer

