#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Template
from .crud import CRUD


class TemplatesListingSection(CRUD):
    model = Template

