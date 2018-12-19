#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models.rendering import ImageFactory
from .crud import CRUD


class ImageFactoriesSection(CRUD):
    model = ImageFactory
