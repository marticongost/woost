#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Style
from .crud import CRUD


class StylesListingSection(CRUD):
    model = Style

