#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Website
from .crud import CRUD


class WebsitesSection(CRUD):
    model = Website

