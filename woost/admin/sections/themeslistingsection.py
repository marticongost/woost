#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .crud import CRUD
from woost.models import Theme


class ThemesListingSection(CRUD):
    model = Theme

