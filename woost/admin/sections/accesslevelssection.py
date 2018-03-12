#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import AccessLevel
from .crud import CRUD


class AccessLevelsSection(CRUD):
    model = AccessLevel

