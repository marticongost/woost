#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Controller
from .crud import CRUD


class ControllersListingSection(CRUD):
    model = Controller

